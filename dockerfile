# Base leve e compatível
FROM python:3.13-slim

# Diretório da app
WORKDIR /app

# Copia dependências
COPY requeriments.txt ./

# Instala dependências
RUN pip install --no-cache-dir -r requeriments.txt

# Copia o restante do código
COPY . .

# Variável de ambiente para a porta do Render
ENV PORT=10000

# Comando padrão (pode mudar)
CMD ["python3", "main.py"]
