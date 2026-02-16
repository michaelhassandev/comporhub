# Migração para Administração no MySQL

## Atualização do Banco de Dados

Para ativar a funcionalidade de administração no MySQL, execute os seguintes comandos SQL no seu banco de dados MySQL:

```sql
-- Adicionar campo is_admin à tabela user
ALTER TABLE user ADD COLUMN is_admin BOOLEAN DEFAULT FALSE;

-- Definir o primeiro usuário como administrador
UPDATE user SET is_admin = TRUE ORDER BY id LIMIT 1;


-- Criar tabela de gêneros
CREATE TABLE genre (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(50) NOT NULL UNIQUE,
  description TEXT
);

-- Adicionar campo genre_id à tabela composition
ALTER TABLE composition ADD COLUMN genre_id INT;

-- Adicionar chave estrangeira
ALTER TABLE composition ADD CONSTRAINT fk_genre_id 
  FOREIGN KEY (genre_id) REFERENCES genre (id) 
  ON DELETE SET NULL;

-- Migrar dados de gênero existentes para a nova tabela
-- Primeiro, insira os gêneros únicos existentes
INSERT INTO genre (name)
SELECT DISTINCT genre FROM composition WHERE genre IS NOT NULL AND genre != '';

-- Depois, atualize as composições com o novo genre_id
UPDATE composition c
JOIN genre g ON c.genre = g.name
SET c.genre_id = g.id
WHERE c.genre IS NOT NULL AND c.genre != '';
```

## Passo-a-passo para a migração

1. Faça backup do seu banco de dados MySQL antes de executar qualquer comando
2. Execute os comandos SQL acima na ordem apresentada
3. Reinicie a aplicação após as alterações no banco de dados
4. Acesse o sistema com o primeiro usuário cadastrado (que agora é administrador)
5. Vá para o painel de administração clicando em "Administração" no menu

## Funcionalidades Administrativas Disponíveis

- **Gerenciar Gêneros**: Adicione, edite e remova gêneros musicais
- **Gerenciar Usuários**: Visualize e edite informações de usuários, incluindo torná-los administradores
- **Painel de Estatísticas**: Veja estatísticas gerais do sistema

## Importante

1. Apenas o usuário administrador tem acesso à área administrativa
2. O primeiro usuário cadastrado é automaticamente definido como administrador
3. Usuários administradores podem designar outros usuários como administradores
4. As composições agora estão vinculadas a gêneros cadastrados no sistema
