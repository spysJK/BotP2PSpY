import qrcode
import uuid
from PIL import Image


def gerar_payload_pix(valor, chave_pix, nome_recebedor="SPYJKP2P", cidade="BR"):
    """
    Gera o código PIX Copia-e-Cola usando EMVCo + BRCode.
    """

    valor_str = f"{valor:.2f}"

    txid = str(uuid.uuid4())[:25]

    payload = (
        "000201"
        "010212"
        "26" + f"{len('0014br.gov.bcb.pix01' + str(len(chave_pix)).zfill(2) + chave_pix)}"
        "0014br.gov.bcb.pix"
        "01" + f"{len(chave_pix):02}{chave_pix}"
        "52040000"
        "5303986"
        f"540{len(valor_str):02}{valor_str}"
        f"5802BR"
        f"59{len(nome_recebedor):02}{nome_recebedor}"
        f"60{len(cidade):02}{cidade}"
        f"62{len('05' + str(len(txid)).zfill(2) + txid):02}"
        "05" + f"{len(txid):02}{txid}"
    )

    def crc16(payload):
        polinomio = 0x1021
        resultado = 0xFFFF
        bytes_payload = bytearray(payload.encode('utf-8'))

        for byte in bytes_payload:
            resultado ^= (byte << 8)
            for _ in range(8):
                if (resultado & 0x8000) > 0:
                    resultado = (resultado << 1) ^ polinomio
                else:
                    resultado <<= 1
                resultado &= 0xFFFF
        return formato_crc(resultado)

    def formato_crc(crc):
        return format(crc, '04X')

    payload_sem_crc = payload + "6304"
    crc = crc16(payload_sem_crc)
    return payload_sem_crc + crc

def gerar_qrcode_pix(payload, caminho_arquivo="qrcode_pix.png"):
    img = qrcode.make(payload)
    img.save(caminho_arquivo)
    return caminho_arquivo
