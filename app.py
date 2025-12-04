import cherrypy
import sqlite3
import os

local_dir = os.path.dirname(os.path.abspath(__file__))
raiz_projeto = os.path.dirname(local_dir)
DB_NAME = os.path.join(raiz_projeto, "database", "equilibramente.db")

class VoluntariosSistema(object):
    
    def get_db_connection(self):
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row 
        return conn

    def carregar_pagina(self, nome_arquivo):
        caminho = os.path.join(raiz_projeto, 'pages', nome_arquivo)
        try:
            with open(caminho, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return f"<h1>Erro: Arquivo '{nome_arquivo}' nao encontrado em pages.</h1>"

    @cherrypy.expose
    def index(self):
        caminho = os.path.join(raiz_projeto, 'index.html')
        try:
            with open(caminho, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return "<h1>Erro: index.html nao encontrado na raiz.</h1>"

    @cherrypy.expose
    def sobre(self): return self.carregar_pagina('sobre.html')
    @cherrypy.expose
    def como_funciona(self): return self.carregar_pagina('como-funciona.html')
    @cherrypy.expose
    def artigos(self): return self.carregar_pagina('artigos.html')
    @cherrypy.expose
    def agendar(self): return self.carregar_pagina('agendar.html')
    @cherrypy.expose
    def voluntarios(self): return self.carregar_pagina('voluntarios.html')

    @cherrypy.expose
    def perfil_carlos(self): return self.carregar_pagina('Voluntarios/Dr-Carlos-Mendes.html')
    @cherrypy.expose
    def perfil_joao(self): return self.carregar_pagina('Voluntarios/Dr-João-Santos.html')
    @cherrypy.expose
    def perfil_claudia(self): return self.carregar_pagina('Voluntarios/Dra-Claudia.html')
    @cherrypy.expose
    def perfil_maria(self): return self.carregar_pagina('Voluntarios/Dra-Maria-Ines.html')

    @cherrypy.expose
    def ser_voluntario(self):
        html = self.carregar_pagina('ser-voluntario.html')
        marcadores = ['__TITULO__', '__ID__', '__NOME__', '__EMAIL__', '__TELEFONE__', 
                      '__CIDADE__', '__REGISTRO__', '__EXPERIENCIA__', '__DIAS__', 
                      '__HORARIOS__', '__MOTIVO__', '__OBSERVACOES__']
        html = html.replace('__TITULO__', 'Seja um Voluntário')
        for m in marcadores:
            html = html.replace(m, '')
        return html

    @cherrypy.expose
    def listar(self):
        conn = self.get_db_connection()
        try:
            dados = conn.execute('SELECT * FROM voluntarios').fetchall()
        except sqlite3.OperationalError:
            return "<h1>Erro: Tabela 'voluntarios' nao encontrada. Verifique o banco.</h1>"
        conn.close()
        
        linhas = ""
        for v in dados:
            linhas += f"""
            <tr>
                <td>{v['id_voluntario']}</td>
                <td>{v['nome_completo']}</td>
                <td>{v['email']}</td>
                <td>{v['especialidade_principal']}</td>
                <td>
                    <a href="editar?id={v['id_voluntario']}" style="color:orange; margin-right:10px;">Editar</a>
                    <a href="excluir?id={v['id_voluntario']}" style="color:red;" onclick="return confirm('Excluir?');">Excluir</a>
                </td>
            </tr>
            """
        
        if not linhas:
            linhas = "<tr><td colspan='5' style='text-align:center'>Nenhum registro.</td></tr>"

        html = self.carregar_pagina('lista-voluntarios.html')
        return html.replace('__LINHAS__', linhas)

    @cherrypy.expose
    def gravar(self, **kwargs):
        conn = self.get_db_connection()
        id_voluntario = kwargs.get('id_voluntario')
        areas = kwargs.get('area_interesse', [])
        area_string = ", ".join(areas) if isinstance(areas, list) else areas 

        try:
            if id_voluntario:
                sql = '''UPDATE voluntarios SET nome_completo=?, email=?, telefone=?, cidade=?, 
                        registro_profissional=?, especialidade_principal=?, experiencia_profissional=?, 
                        area_de_interesse=?, disponibilidade_dia=?, diponibilidade_horario=?, 
                        motivo_voluntariado=?, informacoes_extras=? WHERE id_voluntario=?'''
                params = (kwargs['nome'], kwargs['email'], kwargs['telefone'], kwargs['cidade'],
                    kwargs['registro'], kwargs['especialidade'], kwargs['experiencia'], area_string, 
                    kwargs['dias'], kwargs['horarios'], kwargs['motivo'], kwargs['observacoes'], id_voluntario)
            else:
                sql = '''INSERT INTO voluntarios (nome_completo, email, telefone, cidade, registro_profissional, 
                        especialidade_principal, experiencia_profissional, area_de_interesse, disponibilidade_dia, 
                        diponibilidade_horario, motivo_voluntariado, informacoes_extras) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
                params = (kwargs['nome'], kwargs['email'], kwargs['telefone'], kwargs['cidade'],
                    kwargs['registro'], kwargs['especialidade'], kwargs['experiencia'], area_string, 
                    kwargs['dias'], kwargs['horarios'], kwargs['motivo'], kwargs['observacoes'])
            
            conn.execute(sql, params)
            conn.commit()
        finally:
            conn.close()
            
        raise cherrypy.HTTPRedirect("/listar")

    @cherrypy.expose
    def editar(self, id):
        conn = self.get_db_connection()
        dado = conn.execute('SELECT * FROM voluntarios WHERE id_voluntario = ?', (id,)).fetchone()
        conn.close()
        if not dado: raise cherrypy.HTTPRedirect("/listar")

        html = self.carregar_pagina('ser-voluntario.html')
        html = html.replace('__TITULO__', 'Editar Cadastro')
        html = html.replace('__ID__', str(dado['id_voluntario']))
        html = html.replace('__NOME__', dado['nome_completo'])
        html = html.replace('__EMAIL__', dado['email'])
        html = html.replace('__TELEFONE__', dado['telefone'])
        html = html.replace('__CIDADE__', dado['cidade'])
        html = html.replace('__REGISTRO__', dado['registro_profissional'])
        html = html.replace('__EXPERIENCIA__', dado['experiencia_profissional'])
        html = html.replace('__DIAS__', dado['disponibilidade_dia'])
        html = html.replace('__HORARIOS__', dado['diponibilidade_horario'])
        html = html.replace('__MOTIVO__', dado['motivo_voluntariado'])
        html = html.replace('__OBSERVACOES__', dado['informacoes_extras'])
        
        if dado['especialidade_principal']:
            html = html.replace(f'value="{dado["especialidade_principal"]}"', f'value="{dado["especialidade_principal"]}" selected')
        
        if dado['area_de_interesse']:
            areas = dado['area_de_interesse'].split(", ")
            for area in areas:
                html = html.replace(f'value="{area}"', f'value="{area}" checked')

        return html

    @cherrypy.expose
    def excluir(self, id):
        conn = self.get_db_connection()
        conn.execute('DELETE FROM voluntarios WHERE id_voluntario = ?', (id,))
        conn.commit()
        conn.close()
        raise cherrypy.HTTPRedirect("/listar")

if __name__ == '__main__':
    conf = {
        '/': { 'tools.sessions.on': True, 'tools.staticdir.root': raiz_projeto },
        '/styles': { 'tools.staticdir.on': True, 'tools.staticdir.dir': 'styles' },
        '/images': { 'tools.staticdir.on': True, 'tools.staticdir.dir': 'images' }
    }
    cherrypy.quickstart(VoluntariosSistema(), '/', conf)