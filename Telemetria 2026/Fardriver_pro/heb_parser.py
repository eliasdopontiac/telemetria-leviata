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

        # 1. Pares de Polos (Offset 2 - Byte direto)
        pole_pairs = data[2]
        
        # 2. Correntes (Offset 52 e 92 - Valores de 16 bits que precisam de conversão)
        raw_line = struct.unpack_from('<H', data, 52)[0]
        raw_phase = struct.unpack_from('<H', data, 92)[0]
        line_a = raw_line / 4.0
        phase_a = raw_phase / 4.0
        
        # 3. Sensores e Acelerador (Offset 40 - Campos de Bits Esmagados)
        config_byte = data[40]
        valor_throttle = config_byte & 0x03 
        valor_weaka = (config_byte >> 2) & 0x03

        # NOVO: DUMP HEXADECIMAL PARA DIAGNÓSTICO DO FICHEIRO
        hex_dump = " ".join([f"{b:02X}" for b in data[:120]])

        # Retorna os dados purificados
        return {
            "pole_pairs": pole_pairs,
            "line_curr": line_a,
            "phase_curr": phase_a,
            "throttle_mode": valor_throttle,
            "weaka_level": valor_weaka,
            "raw_dump": hex_dump
        }

    @staticmethod
    def save_file(template_path, output_path, config_dict):
        """
        Lê um ficheiro .heb base (template), altera os parâmetros desejados
        (Polos, Correntes, Acelerador, WeakA) e guarda como um novo ficheiro .heb
        pronto a ser "injetado" na controladora Fardriver.
        """
        with open(template_path, 'rb') as f:
            # Usamos bytearray porque bytes em Python são imutáveis
            data = bytearray(f.read())
        
        if len(data) < 100:
            raise ValueError("O ficheiro template .heb é inválido.")

        # 1. Atualizar Pares de Polos
        if "pole_pairs" in config_dict:
            data[2] = int(config_dict["pole_pairs"]) & 0xFF
            
        # 2. Atualizar Correntes (Fazemos o inverso: multiplicamos por 4)
        if "line_curr" in config_dict:
            struct.pack_into('<H', data, 52, int(config_dict["line_curr"] * 4))
        if "phase_curr" in config_dict:
            struct.pack_into('<H', data, 92, int(config_dict["phase_curr"] * 4))
            
        # 3. Atualizar Sensores e Acelerador (Offset 40)
        if "throttle_mode" in config_dict and "weaka_level" in config_dict:
            old_byte = data[40]
            
            # Limpamos apenas os 4 bits da direita (Acelerador e WeakA)
            # usando a máscara 0xF0 (que em binário é 1111 0000)
            base_byte = old_byte & 0xF0
            
            # Preparamos os novos bits
            t_bits = config_dict["throttle_mode"] & 0x03
            w_bits = (config_dict["weaka_level"] & 0x03) << 2 # Empurramos 2 casas para a esquerda
            
            # Juntamos tudo no novo byte
            data[40] = base_byte | w_bits | t_bits

        # Escrevemos a matriz de bytes final no novo ficheiro
        with open(output_path, 'wb') as f:
            f.write(data)
            
        return True