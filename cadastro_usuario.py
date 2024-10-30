import csv
import json
import os
import re
import configparser
from datetime import datetime
import random
import string


config = configparser.ConfigParser()
config.read('config.ini')

DATA_FILE_CSV = config.get('settings', 'data_file_csv', fallback='cadastro.csv')
DATA_FILE_JSON = config.get('settings', 'data_file_json', fallback='cadastro.json')
LOG_FILE = 'log.txt'

class Usuario:
    """Classe que representa um usuário."""
    def __init__(self, nome, email):
        self.nome = nome
        self.email = email

    def to_dict(self):
        return {"Nome": self.nome, "Email": self.email}

class SistemaCadastro:
    """Class que representa o sistema de cadastro de usuários."""
    def __init__(self):
        self.usuarios = []

    def log_event(self, message):
        """Registra eventos em um arquivo de log."""
        with open(LOG_FILE, mode='a', encoding='utf-8') as log_file:
            log_file.write(f"{datetime.now()}: {message}\n")

    def validar_email(self, email):
        """Valida o formato de um endereço de e-mail."""
        padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(padrao, email) is not None

    def validar_nome(self, nome):
        """Verifica se o nome não está vazio ou contém apenas espaços."""
        return bool(nome.strip())

    def carregar_usuarios(self, formato='csv'):
        """Carrega usuários de um arquivo, seja CSV ou JSON."""
        try:
            if formato == 'csv':
                if not os.path.isfile(DATA_FILE_CSV):
                    return []
                with open(DATA_FILE_CSV, mode="r", encoding='utf-8') as arquivo:
                    reader = csv.DictReader(arquivo)
                    self.usuarios = [Usuario(linha['Nome'], linha['Email']) for linha in reader]
            elif formato == 'json':
                if not os.path.isfile(DATA_FILE_JSON):
                    return []
                with open(DATA_FILE_JSON, mode="r", encoding='utf-8') as arquivo:
                    data = json.load(arquivo)
                    self.usuarios = [Usuario(usuario['Nome'], usuario['Email']) for usuario in data]
        except Exception as e:
            self.log_event(f"Erro ao carregar usuários: {e}")
            print(f"Erro ao carregar usuários: {e}")

    def salvar_usuarios(self, formato='csv'):
        """Salva a lista de usuários em um arquivo, seja CSV ou JSON."""
        try:
            if formato == 'csv':
                with open(DATA_FILE_CSV, mode="w", newline='', encoding='utf-8') as arquivo:
                    writer = csv.DictWriter(arquivo, fieldnames=["Nome", "Email"])
                    writer.writeheader()
                    writer.writerows(usuario.to_dict() for usuario in self.usuarios)
            elif formato == 'json':
                with open(DATA_FILE_JSON, mode="w", encoding='utf-8') as arquivo:
                    json.dump([usuario.to_dict() for usuario in self.usuarios], arquivo, indent=4)
        except Exception as e:
            self.log_event(f"Erro ao salvar usuários: {e}")
            print(f"Erro ao salvar usuários: {e}")

    def cadastrar_usuario(self, nome, email):
        """Cadastra um novo usuário no sistema."""
        if not self.validar_nome(nome):
            self.mensagem_erro("Nome inválido. O nome não pode estar vazio.")
            return False
        
        if not self.validar_email(email):
            self.mensagem_erro("Email inválido. Tente novamente.")
            return False

        if any(usuario.email == email for usuario in self.usuarios):
            self.mensagem_erro("Um usuário com este email já está cadastrado.")
            return False
        
        usuario = Usuario(nome, email)
        self.usuarios.append(usuario)
        self.salvar_usuarios()
        self.log_event(f"Usuário '{nome}' com email '{email}' cadastrado.")
        self.mensagem_sucesso(f"Usuário '{nome}' cadastrado com sucesso!")
        return True

    def listar_usuarios(self):
        """Lista todos os usuários cadastrados."""
        if not self.usuarios:
            print("Nenhum usuário cadastrado.")
            return
        
        print("\n=== Usuários Cadastrados ===")
        print(f"{'Nome':<30} | {'Email':<30}")
        print("-" * 62)
        for usuario in self.usuarios:
            print(f"{usuario.nome:<30} | {usuario.email:<30}")

    def apagar_usuario(self, email):
        """Remove um usuário pelo seu email."""
        for usuario in self.usuarios:
            if usuario.email == email:
                self.usuarios.remove(usuario)
                self.salvar_usuarios()
                self.log_event(f"Usuário com email '{email}' removido.")
                self.mensagem_sucesso(f"Usuário com email '{email}' removido com sucesso!")
                return
        
        self.mensagem_erro(f"Nenhum usuário encontrado com o email '{email}'.")

    def buscar_usuario(self, criterio):
        """Busca um usuário pelo nome ou email."""
        encontrados = [usuario for usuario in self.usuarios if criterio.lower() in usuario.nome.lower() or criterio.lower() in usuario.email.lower()]
        
        if not encontrados:
            self.mensagem_erro(f"Nenhum usuário encontrado com '{criterio}'.")
            return
        
        print(f"\n=== Resultados da Busca por '{criterio}' ===")
        for usuario in encontrados:
            print(f"Usuário encontrado: Nome: {usuario.nome}, Email: {usuario.email}")

    def atualizar_usuario(self, email, novo_nome=None, novo_email=None):
        """Atualiza o nome ou email de um usuário existente."""
        for usuario in self.usuarios:
            if usuario.email == email:
                if novo_nome and self.validar_nome(novo_nome):
                    usuario.nome = novo_nome
                if novo_email and self.validar_email(novo_email):
                    usuario.email = novo_email
                
                self.salvar_usuarios()
                self.log_event(f"Usuário com email '{email}' atualizado para nome '{usuario.nome}' e email '{usuario.email}'.")
                self.mensagem_sucesso(f"Usuário com email '{email}' atualizado com sucesso!")
                return
            
        self.mensagem_erro(f"Nenhum usuário encontrado com o email '{email}'.")

    def mensagem_erro(self, mensagem):
        """Exibe uma mensagem de erro."""
        print(f"Erro: {mensagem}")

    def mensagem_sucesso(self, mensagem):
        """Exibe uma mensagem de sucesso."""
        print(f"Sucesso: {mensagem}")

    def gerar_nome_aleatorio(self):
        """Gera um nome aleatório simples."""
        nomes = ['Ana', 'João', 'Maria', 'Pedro', 'Lucas', 'Fernanda', 'Juliana', 'Carlos']
        sobrenomes = ['Silva', 'Souza', 'Oliveira', 'Santos', 'Pereira', 'Lima', 'Eduarda', 'Miguel', 'Guilherme', 'Batata']
        return f"{random.choice(nomes)} {random.choice(sobrenomes)}"

    def gerar_email_aleatorio(self, nome):
        """Gera um e-mail aleatório baseado no nome."""
        dominio = ''.join(random.choices(string.ascii_lowercase, k=5)) + "gmail.com"
        nome_usuario = nome.replace(" ", ".").lower()  
        return f"{nome_usuario}@{dominio}"

    def gerar_usuario_aleatorio(self):
        """Gera um usuário com nome e email aleatórios."""
        nome = self.gerar_nome_aleatorio()
        email = self.gerar_email_aleatorio(nome)
        while any(usuario.email == email for usuario in self.usuarios):
            email = self.gerar_email_aleatorio(nome)  

        self.cadastrar_usuario(nome, email)

def menu(sistema):
    """Exibe o menu principal do sistema."""
    options = {
        "1": "Cadastrar usuário",
        "2": "Listar usuários",
        "3": "Apagar usuário",
        "4": "Buscar usuário",
        "5": "Atualizar usuário",
        "6": "Gerar um usuário aleatório",
        "7": "Sair"
    }
    
    while True:
        print("\n=== Sistema de Cadastro ===")
        for key, value in options.items():
            print(f"{key}. {value}")
        
        escolha = input("Escolha uma opção: ")

        if escolha == "1":
            nome = input("Digite o seu nome: ")
            email = input("Digite o seu email: ")
            sistema.cadastrar_usuario(nome, email)
        elif escolha == "2":
            sistema.carregar_usuarios()
            sistema.listar_usuarios()
        elif escolha == "3":
            email = input("Digite o email do usuário a ser removido: ")
            sistema.apagar_usuario(email)
        elif escolha == "4":
            criterio = input("Digite o nome ou email para buscar: ")
            sistema.buscar_usuario(criterio)
        elif escolha == "5":
            email = input("Digite o email do usuário a ser atualizado: ")
            novo_nome = input("Digite o novo nome (deixe vazio para não alterar): ")
            novo_email = input("Digite o novo email (deixe vazio para não alterar): ")
            sistema.atualizar_usuario(email, novo_nome.strip() or None, novo_email.strip() or None)
        elif escolha == "6":
            sistema.gerar_usuario_aleatorio()
        elif escolha == "7":
            print("Saindo do sistema...")
            break
        else:
            print("Erro: Opção inválida! Tente novamente.")

if __name__ == "__main__":
    sistema = SistemaCadastro()
    sistema.carregar_usuarios()
    menu(sistema)
