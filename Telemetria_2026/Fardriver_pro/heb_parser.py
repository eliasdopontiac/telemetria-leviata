import struct


class HebParser:
    """
    Módulo responsável por ler, descodificar, analisar e CRIAR ficheiros de backup (.heb)
    da controladora Fardriver.
    Isola a lógica binária (bytes, offsets e bitmasks) do resto da aplicação.
    """

    @staticmethod
    def parse_file(filepath: str) -> dict:
        """
        Abre o ficheiro .heb, extrai TODOS os parâmetros conhecidos e retorna
        um dicionário limpo com os valores prontos a usar pela UI.

        Estrutura do ficheiro .heb:
            Cada bloco ocupa 12 bytes. O byte_offset de um word_address é:
                byte_offset = word_address * 2
        """
        with open(filepath, "rb") as f:
            data = f.read()

        if len(data) < 200:
            raise ValueError("Ficheiro .heb corrompido ou pequeno demais.")

        def word(offset):
            return struct.unpack_from("<H", data, offset)[0]

        def sword(offset):
            return struct.unpack_from("<h", data, offset)[0]

        def byte(offset):
            return data[offset]

        result = {}

        # ── Addr12 (word 0x12, byte offset 36) ──────────────────────────
        base = 0x12 * 2  # = 36
        result["pole_pairs"] = byte(base + 4)
        result["max_speed"] = word(base + 6)
        result["rated_power"] = word(base + 8)
        result["rated_voltage"] = word(base + 10) / 10.0

        # ── Addr18 (word 0x18, byte offset 48) ──────────────────────────
        base = 0x18 * 2  # = 48
        result["rated_speed"] = word(base + 0)
        result["max_line_curr"] = word(base + 2) / 4.0
        cfg26l = byte(base + 4)
        result["follow_config"] = cfg26l & 0x03
        result["throttle_response"] = (cfg26l >> 2) & 0x03
        result["weaka"] = (cfg26l >> 4) & 0x03

        # ── Addr0C (word 0x0C, byte offset 24) ──────────────────────────
        base = 0x0C * 2  # = 24
        result["phase_offset"] = sword(base + 0) / 10.0
        result["zero_batt_coeff"] = sword(base + 2)
        result["full_batt_coeff"] = sword(base + 4)
        result["start_ki"] = byte(base + 6)
        result["mid_ki"] = byte(base + 7)
        result["max_ki"] = byte(base + 8)
        result["start_kp"] = byte(base + 9)
        result["mid_kp"] = byte(base + 10)
        result["max_kp"] = byte(base + 11)

        # ── Addr06 (word 0x06, byte offset 12) ──────────────────────────
        base = 0x06 * 2  # = 12
        result["throttle_low"] = byte(base + 6) / 20.0
        result["throttle_high"] = byte(base + 7) / 20.0
        cfg11l = byte(base + 10)
        result["temp_sensor"] = (cfg11l >> 1) & 0x07
        result["brake_config"] = cfg11l & 0x01
        cfg11h = byte(base + 11)
        result["direction"] = (cfg11h >> 7) & 0x01

        # ── Addr1E (word 0x1E, byte offset 60) ──────────────────────────
        base = 0x1E * 2  # = 60
        result["low_vol_protect"] = word(base + 2) / 10.0

        # ── Addr24 (word 0x24, byte offset 72) ──────────────────────────
        base = 0x24 * 2  # = 72
        result["max_phase_curr"] = word(base + 4) / 4.0
        result["back_speed"] = word(base + 8)
        result["low_speed"] = word(base + 10)

        # ── Addr2A (word 0x2A, byte offset 84) ──────────────────────────
        base = 0x2A * 2  # = 84
        result["max_phase_curr2"] = word(base + 6) / 4.0

        # ── Addr30 (word 0x30, byte offset 96) ──────────────────────────
        base = 0x30 * 2  # = 96
        result["stop_back_curr"] = word(base + 0)
        result["max_back_curr"] = word(base + 2)

        # ── Addr88 (word 0x88, byte offset 272) — tabela corrente por RPM
        base = 0x88 * 2  # = 272
        if len(data) > base + 12:
            labels_low = [
                "min",
                "500",
                "1000",
                "1500",
                "2000",
                "2500",
                "3000",
                "3500",
                "4000",
                "4500",
                "5000",
                "5500",
            ]
            ratio_table_low = {labels_low[i]: byte(base + i) for i in range(12)}

            # ── Addr8E (word 0x8E, byte offset 284) — tabela corrente cont. + início regen
            base_8e = 0x8E * 2  # = 284
            labels_high = ["6000", "6500", "7000", "7500", "8000", "8500", "9000", "max"]
            ratio_table_high = {labels_high[i]: byte(base_8e + i) for i in range(8)}
            
            # ── Consolidar tabela unificada (18 pontos)
            rpm_labels = [
                "min", "500", "1000", "1500", "2000", "2500", "3000",
                "3500", "4000", "4500", "5000", "5500", "6000", "6500",
                "7000", "7500", "8000", "max"
            ]
            ratio_table = {}
            for i in range(12):
                ratio_table[rpm_labels[i]] = ratio_table_low[labels_low[i]]
            for i in range(8):
                ratio_table[rpm_labels[12 + i]] = ratio_table_high[labels_high[i]]
            
            result["ratio_table"] = ratio_table
            
            # Tabela de regen — nratio_table (18 pontos, valores signed)
            nratio_a = {
                f"n{i}": struct.unpack_from("b", data, base_8e + 8 + i)[0]
                for i in range(4)
            }
            
            # ── Addr94 (word 0x94, byte offset 296) — regen cont.
            base_94 = 0x94 * 2  # = 296
            nratio_b = {
                f"n{i + 4}": struct.unpack_from("b", data, base_94 + i)[0]
                for i in range(12)
            }
            
            # ── Addr9A (word 0x9A, byte offset 308) — regen cont. + AN/LM
            base_9a = 0x9A * 2  # = 308
            nratio_c = {
                f"n{i + 16}": struct.unpack_from("b", data, base_9a + i)[0]
                for i in range(4)
            }
            result["AN"] = byte(base_9a + 4) & 0x0F
            result["LM"] = byte(base_9a + 5) & 0x1F
            
            # Consolidar tabela unificada de regen (18 pontos)
            nratio_combined = {}
            nratio_combined.update(nratio_a)
            nratio_combined.update(nratio_b)
            # Para nratio_c, usar os 2 primeiros pontos (n16 e n17)
            for i in range(2):
                nratio_combined[f"n{16 + i}"] = struct.unpack_from("b", data, base_9a + i)[0]
            
            result["nratio_table"] = nratio_combined

        # ── Addr82 (word 0x82, byte offset 260) — hardware/software version
        base = 0x82 * 2  # = 260
        if len(data) > base + 12:
            result["motor_temp_protect"] = byte(base + 4)
            result["motor_temp_restore"] = byte(base + 5)
            result["mos_temp_protect"] = byte(base + 6)
            result["mos_temp_restore"] = byte(base + 7)
            hw = byte(base + 9)
            result["hardware_version"] = chr(hw) if 32 <= hw <= 126 else "?"
            sw = byte(base + 10)
            result["software_version"] = chr(sw) if 32 <= sw <= 126 else "?"

        # ── Compatibilidade com código legado ───────────────────────────
        result["line_curr"] = result.get("max_line_curr", 0)
        result["phase_curr"] = result.get("max_phase_curr", 0)
        result["throttle_mode"] = result.get("throttle_response", 0)
        result["weaka_level"] = result.get("weaka", 0)

        # ── Dump hex dos primeiros 120 bytes para diagnóstico ────────────
        result["raw_dump"] = " ".join(f"{b:02X}" for b in data[:120])

        return result

    @staticmethod
    def save_file(template_path: str, output_path: str, config_dict: dict) -> bool:
        """
        Lê um ficheiro .heb base (template), aplica TODOS os parâmetros presentes
        em config_dict e guarda o resultado em output_path.

        Apenas os campos presentes em config_dict são modificados; os restantes
        bytes do template são preservados intactos.
        """
        with open(template_path, "rb") as f:
            data = bytearray(f.read())

        if len(data) < 200:
            raise ValueError("Template .heb inválido.")

        def set_word(offset, val):
            struct.pack_into("<H", data, offset, int(val) & 0xFFFF)

        def set_sword(offset, val):
            struct.pack_into("<h", data, offset, int(val))

        def set_byte(offset, val):
            data[offset] = int(val) & 0xFF

        # ── Addr12 ──────────────────────────────────────────────────────
        base = 0x12 * 2
        if "pole_pairs" in config_dict:
            set_byte(base + 4, config_dict["pole_pairs"])
        if "max_speed" in config_dict:
            set_word(base + 6, config_dict["max_speed"])
        if "rated_power" in config_dict:
            set_word(base + 8, config_dict["rated_power"])
        if "rated_voltage" in config_dict:
            set_word(base + 10, int(config_dict["rated_voltage"] * 10))

        # ── Addr18 ──────────────────────────────────────────────────────
        base = 0x18 * 2
        if "rated_speed" in config_dict:
            set_word(base + 0, config_dict["rated_speed"])
        if "max_line_curr" in config_dict:
            set_word(base + 2, int(config_dict["max_line_curr"] * 4))
        if any(
            k in config_dict for k in ("follow_config", "throttle_response", "weaka")
        ):
            cfg26l = data[base + 4]
            fc = config_dict.get("follow_config", cfg26l & 0x03)
            tr = config_dict.get("throttle_response", (cfg26l >> 2) & 0x03)
            wa = config_dict.get("weaka", (cfg26l >> 4) & 0x03)
            rxd = (cfg26l >> 6) & 0x03
            set_byte(base + 4, fc | (tr << 2) | (wa << 4) | (rxd << 6))

        # ── Addr0C ──────────────────────────────────────────────────────
        base = 0x0C * 2
        if "phase_offset" in config_dict:
            set_sword(base + 0, int(config_dict["phase_offset"] * 10))
        if "zero_batt_coeff" in config_dict:
            set_sword(base + 2, config_dict["zero_batt_coeff"])
        if "full_batt_coeff" in config_dict:
            set_sword(base + 4, config_dict["full_batt_coeff"])
        if "start_ki" in config_dict:
            set_byte(base + 6, config_dict["start_ki"])
        if "mid_ki" in config_dict:
            set_byte(base + 7, config_dict["mid_ki"])
        if "max_ki" in config_dict:
            set_byte(base + 8, config_dict["max_ki"])
        if "start_kp" in config_dict:
            set_byte(base + 9, config_dict["start_kp"])
        if "mid_kp" in config_dict:
            set_byte(base + 10, config_dict["mid_kp"])
        if "max_kp" in config_dict:
            set_byte(base + 11, config_dict["max_kp"])

        # ── Addr06 ──────────────────────────────────────────────────────
        base = 0x06 * 2
        if "throttle_low" in config_dict:
            set_byte(base + 6, int(config_dict["throttle_low"] * 20))
        if "throttle_high" in config_dict:
            set_byte(base + 7, int(config_dict["throttle_high"] * 20))
        if any(k in config_dict for k in ("temp_sensor", "brake_config")):
            cfg11l = data[base + 10]
            ts = config_dict.get("temp_sensor", (cfg11l >> 1) & 0x07)
            bc = config_dict.get("brake_config", cfg11l & 0x01)
            set_byte(base + 10, bc | (ts << 1))
        if "direction" in config_dict:
            cfg11h = data[base + 11]
            dr = config_dict.get("direction", (cfg11h >> 7) & 0x01)
            set_byte(base + 11, (cfg11h & 0x7F) | (dr << 7))

        # ── Addr1E ──────────────────────────────────────────────────────
        base = 0x1E * 2
        if "low_vol_protect" in config_dict:
            set_word(base + 2, int(config_dict["low_vol_protect"] * 10))

        # ── Addr24 ──────────────────────────────────────────────────────
        base = 0x24 * 2
        if "max_phase_curr" in config_dict:
            set_word(base + 4, int(config_dict["max_phase_curr"] * 4))
        if "back_speed" in config_dict:
            set_word(base + 8, config_dict["back_speed"])
        if "low_speed" in config_dict:
            set_word(base + 10, config_dict["low_speed"])

        # ── Addr2A ──────────────────────────────────────────────────────
        base = 0x2A * 2
        if "max_phase_curr2" in config_dict:
            set_word(base + 6, int(config_dict["max_phase_curr2"] * 4))

        # ── Addr30 ──────────────────────────────────────────────────────
        base = 0x30 * 2
        if "stop_back_curr" in config_dict:
            set_word(base + 0, config_dict["stop_back_curr"])
        if "max_back_curr" in config_dict:
            set_word(base + 2, config_dict["max_back_curr"])

        # ── Addr88 — tabela corrente (RPM baixo) ─────────────────────────
        base = 0x88 * 2
        if "ratio_table" in config_dict and len(data) > base + 12:
            labels = [
                "min",
                "500",
                "1000",
                "1500",
                "2000",
                "2500",
                "3000",
                "3500",
                "4000",
                "4500",
                "5000",
                "5500",
            ]
            for i, lbl in enumerate(labels):
                if lbl in config_dict["ratio_table"]:
                    set_byte(base + i, config_dict["ratio_table"][lbl])

        # ── Addr8E — tabela corrente (RPM alto) ──────────────────────────
        base = 0x8E * 2
        if "ratio_table" in config_dict and len(data) > base + 8:
            labels_h = ["6000", "6500", "7000", "7500", "8000", "8500", "9000", "max"]
            for i, lbl in enumerate(labels_h):
                if lbl in config_dict["ratio_table"]:
                    set_byte(base + i, config_dict["ratio_table"][lbl])

        # ── Addr9A — AN/LM ───────────────────────────────────────────────
        base = 0x9A * 2
        if "AN" in config_dict and len(data) > base + 5:
            set_byte(
                base + 4, (data[base + 4] & 0xF0) | (int(config_dict["AN"]) & 0x0F)
            )
        if "LM" in config_dict and len(data) > base + 6:
            set_byte(
                base + 5, (data[base + 5] & 0xE0) | (int(config_dict["LM"]) & 0x1F)
            )

        # ── Addr82 — temperaturas e versões ──────────────────────────────
        base = 0x82 * 2
        if len(data) > base + 12:
            if "motor_temp_protect" in config_dict:
                set_byte(base + 4, config_dict["motor_temp_protect"])
            if "motor_temp_restore" in config_dict:
                set_byte(base + 5, config_dict["motor_temp_restore"])
            if "mos_temp_protect" in config_dict:
                set_byte(base + 6, config_dict["mos_temp_protect"])
            if "mos_temp_restore" in config_dict:
                set_byte(base + 7, config_dict["mos_temp_restore"])

        with open(output_path, "wb") as f:
            f.write(data)

        return True
