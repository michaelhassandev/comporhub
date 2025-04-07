# Migração para Upload de Arquivos MP3 no MySQL

## Atualização do Banco de Dados

Execute os seguintes comandos SQL para adicionar suporte a arquivos MP3 às composições:

```sql
-- Adicionar campos para armazenar arquivos de áudio
ALTER TABLE composition ADD COLUMN audio_file VARCHAR(255);
ALTER TABLE composition ADD COLUMN audio_file_size INT;
```

## Configuração do Diretório de Upload

1. Crie um diretório para armazenar os arquivos de áudio:
   ```
   mkdir -p static/uploads/audio
   ```

2. Certifique-se de que o diretório tenha permissões de escrita:
   ```
   chmod 755 -R static/uploads/audio
   ```

## Limitações e Considerações

1. **Tamanho Máximo**: O sistema limita o upload a arquivos de até 3MB. Esta limitação serve para:
   - Evitar tempos de upload excessivos
   - Economizar espaço de armazenamento
   - Facilitar o streaming rápido dos arquivos de áudio

2. **Formatos Suportados**: Apenas arquivos MP3 são aceitos.

3. **Gerenciamento de Arquivos**:
   - Quando uma composição é excluída, o arquivo de áudio associado também é removido
   - Ao atualizar um arquivo de áudio existente, o arquivo anterior é excluído automaticamente

4. **URLs de Áudio**:
   - Os arquivos de áudio são acessados via URL segura: `/audio/<composition_id>`
   - Esta abordagem evita o acesso direto aos arquivos e verifica permissões do usuário

## Como usar

1. Ao criar ou editar uma composição, use o campo "Arquivo de Áudio" para fazer upload do arquivo MP3
2. Após salvar, o arquivo ficará disponível na página de detalhes da composição
3. Um player de áudio será exibido automaticamente para arquivos carregados
