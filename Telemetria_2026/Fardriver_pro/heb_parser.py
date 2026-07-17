import struct

class HebParser:
    """
    Módulo responsável por ler, descodificar, analisar e CRIAR ficheiros de backup (.heb)
    da controladora Fardriver.
    Isola a lógica binária (bytes, offsets e bitmasks) do resto da aplicação.
    """
    
    @staticmethod
    def parse_file(filepath):
        """
        Abre o ficheiro .heb, extrai as configurações e retorna um dicionário
        limpo com os valores prontos a usar pela UI.
        """
        with open(filepath, 'rb') as f:
            data = f.read()
        
        if len(data) < 100:
            raise ValueError("Ficheiro .heb corrompido ou demasiado pequeno.")

        # offsets calculados com base nos blocos de 12 bytes definidos na controladora Fardriver
        
        # 1. Addr12 (Bloco 3 - Offset 36)
        pole_pairs = data[36 + 4]
        max_speed = struct.unpack_from('<H', data, 36 + 6)[0]
        rated_power = struct.unpack_from('<H', data, 36 + 8)[0]
        rated_voltage = struct.unpack_from('<H', data, 36 + 10)[0] / 10.0
        
        # 2. Addr18 (Bloco 4 - Offset 48)
        rated_speed = struct.unpack_from('<H', data, 48 + 0)[0]
        max_line_curr = struct.unpack_from('<H', data, 48 + 2)[0] / 4.0
        cfg26l = data[48 + 4]
        throttle_response = (cfg26l >> 2) & 0x03
        weaka = (cfg26l >> 4) & 0x03
        
        # 3. Addr1E (Bloco 5 - Offset 60)
        low_vol_protect = struct.unpack_from('<H', data, 60 + 2)[0] / 10.0
        
        # 4. Addr24 (Bloco 6 - Offset 72)
        max_phase_curr = struct.unpack_from('<H', data, 72 + 4)[0] / 4.0

        # DUMP HEXADECIMAL PARA DIAGNÓSTICO
        hex_dump = " ".join([f"{b:02X}" for b in data[:120]])

        # Retorna chaves sincronizadas tanto com a aba de parâmetros gerais quanto com os sliders rápidos
        return {
            "pole_pairs": pole_pairs,
            "max_speed": max_speed,
            "rated_power": rated_power,
            "rated_voltage": rated_voltage,
            "rated_speed": rated_speed,
            "max_line_curr": max_line_curr,
            "line_curr": max_line_curr, # Retrocompatibilidade
            "max_phase_curr": max_phase_curr,
            "phase_curr": max_phase_curr, # Retrocompatibilidade
            "throttle_response": throttle_response,
            "throttle_mode": throttle_response, # Retrocompatibilidade
            "weaka": weaka,
            "weaka_level": weaka, # Retrocompatibilidade
            "low_vol_protect": low_vol_protect,
            "raw_dump": hex_dump
        }

    @staticmethod
    def save_file(template_path, output_path, config_dict):
        """
        Lê um ficheiro .heb base (template), altera os parâmetros desejados
        e guarda como um novo ficheiro .heb pronto a ser carregado.
        """
        with open(template_path, 'rb') as f:
            data = bytearray(f.read())
        
        if len(data) < 100:
            raise ValueError("O ficheiro template .heb é inválido.")

        # 1. Atualizar Pares de Polos (Addr12, byte 4)
        if "pole_pairs" in config_dict:
            data[36 + 4] = int(config_dict["pole_pairs"]) & 0xFF
            
        # 2. Atualizar Correntes de Linha (Addr18, bytes 2-3)
        if "max_line_curr" in config_dict:
            struct.pack_into('<H', data, 48 + 2, int(config_dict["max_line_curr"] * 4))
        elif "line_curr" in config_dict:
            struct.pack_into('<H', data, 48 + 2, int(config_dict["line_curr"] * 4))

        # 3. Atualizar Correntes de Fase (Addr24, bytes 4-5)
        if "max_phase_curr" in config_dict:
            struct.pack_into('<H', data, 72 + 4, int(config_dict["max_phase_curr"] * 4))
        elif "phase_curr" in config_dict:
            struct.pack_into('<H', data, 72 + 4, int(config_dict["phase_curr"] * 4))
            
        # 4. Atualizar Acelerador e WeakA (Addr18, byte 4)
        has_throttle = "throttle_response" in config_dict or "throttle_mode" in config_dict
        has_weaka = "weaka" in config_dict or "weaka_level" in config_dict
        if has_throttle or has_weaka:
            old_byte = data[48 + 4]
            # Limpa os bits de throttle e weaka (preserva follow_config nos bits 0-1)
            base_byte = old_byte & 0x03
            
            t_val = config_dict.get("throttle_response", config_dict.get("throttle_mode", 0))
            w_val = config_dict.get("weaka", config_dict.get("weaka_level", 0))
            
            t_bits = (int(t_val) & 0x03) << 2
            w_bits = (int(w_val) & 0x03) << 4
            
            data[48 + 4] = base_byte | t_bits | w_bits

        with open(output_path, 'wb') as f:
            f.write(data)
            
        return True