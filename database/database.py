import sqlite3

DB_NAME = "equilibramente.db"

SQL_CREATE_VOLUNTARIOS = """
CREATE TABLE IF NOT EXISTS "voluntarios" (
	"id_voluntario"	INTEGER NOT NULL,
	"nome_completo"	VARCHAR(100) NOT NULL,
	"email"	VARCHAR(100) NOT NULL,
	"telefone"	VARCHAR(15) NOT NULL,
	"cidade"	VARCHAR(80) NOT NULL,
	"registro_profissional"	VARCHAR(30) NOT NULL,
	"especialidade_principal"	VARCHAR(100) NOT NULL,
	"experiencia_profissional"	TEXT NOT NULL,
	"area_de_interesse"	VARCHAR(150),
	"disponibilidade_dia"	VARCHAR(100) NOT NULL,
	"diponibilidade_horario"	VARCHAR(100) NOT NULL,
	"motivo_voluntariado"	TEXT,
	"informacoes_extras"	TEXT,
	PRIMARY KEY("id_voluntario" AUTOINCREMENT)
);
"""

def criar_tabela_voluntarios():
   
    print(f"Iniciando configuração do banco de dados '{DB_NAME}'...")
    conn = None 
    try:
       
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        print("Criando tabela 'voluntarios' (se não existir)...")
   
        cursor.execute(SQL_CREATE_VOLUNTARIOS)

  
        conn.commit()
        print("Tabela 'voluntarios' verificada/criada com sucesso!")

    except sqlite3.Error as e:
        print(f"Ocorreu um erro ao configurar o banco de dados: {e}")
    finally:
        
        if conn:
            conn.close()
            print(f"Conexão com '{DB_NAME}' fechada.")

if __name__ == "__main__":

    criar_tabela_voluntarios()