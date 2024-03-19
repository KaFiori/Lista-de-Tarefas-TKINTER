import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sqlite3
from datetime import datetime


class Tarefa:
    def __init__(self, descricao, data_inicio, data_fim, status):
        self.descricao = descricao
        self.data_inicio = data_inicio
        self.data_fim = data_fim
        self.status = status

class ListaDeTarefasApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Stark Industries - Lista de Tarefas ")
        self.root.configure(bg='black')
        self.tarefas = []

        # Conectar ao banco de dados SQLite
        self.conn = sqlite3.connect("tarefas.db")
        self.criar_tabela()

        # Criar variáveis Tkinter
        self.descricao_var = tk.StringVar()
        self.data_inicio_var = tk.StringVar()
        self.data_fim_var = tk.StringVar()
        self.status_var = tk.StringVar()
        self.status_var.set("A Fazer")

        # Criar widgets
        self.label_descricao = tk.Label(root, text="Descrição:", bg= "black", fg= "white")
        self.entry_descricao = tk.Entry(root, textvariable=self.descricao_var)

        self.label_data_inicio = tk.Label(root, text="Data de Início (dd/mm/aaaa):", bg= "black", fg= "white")
        self.entry_data_inicio = tk.Entry(root, textvariable=self.data_inicio_var)

        self.label_data_fim = tk.Label(root, text="Data de Fim (dd/mm/aaaa):", bg= "black", fg= "white")
        self.entry_data_fim = tk.Entry(root, textvariable=self.data_fim_var)

        self.label_status = tk.Label(root, text="Status:", bg= "black", fg= "white")
        self.combobox_status = ttk.Combobox(root, values=["A Fazer", "Em Andamento", "Concluído"], textvariable=self.status_var)

        self.btn_adicionar = tk.Button(root, text="Adicionar Tarefa", command=self.adicionar_tarefa, bg= "gray", fg= "white")
        self.btn_listar = tk.Button(root, text="Listar Tarefas", command=self.exibir_lista_tarefas, bg= "gray", fg= "white")
        self.btn_remover_concluidas = tk.Button(root, text="Remover Tarefas Concluídas", command=self.remover_tarefas_concluidas, bg= "red", fg= "white")

        # Posicionar widgets na janela
        self.label_descricao.grid(row=0, column=0, padx=20, pady=10, sticky=tk.E)
        self.entry_descricao.grid(row=0, column=1, padx=10, pady=5)

        self.label_data_inicio.grid(row=1, column=0, padx=20, pady=10, sticky=tk.E)
        self.entry_data_inicio.grid(row=1, column=1, padx=10, pady=5)

        self.label_data_fim.grid(row=2, column=0, padx=10, pady=5, sticky=tk.E)
        self.entry_data_fim.grid(row=2, column=1, padx=10, pady=5)

        self.label_status.grid(row=3, column=0, padx=10, pady=5, sticky=tk.E)
        self.combobox_status.grid(row=3, column=1, padx=10, pady=5)

        self.btn_adicionar.grid(row=4, column=0, columnspan=2, pady=10)
        self.btn_listar.grid(row=5, column=0, columnspan=2, pady=10)
        self.btn_remover_concluidas.grid(row=6, column=0, columnspan=2, pady=10)

    def criar_tabela(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS tarefas (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          descricao TEXT NOT NULL,
                          data_inicio DATE NOT NULL,
                          data_fim DATE NOT NULL,
                          status TEXT NOT NULL)''')
        self.conn.commit()

    def adicionar_tarefa(self):
        descricao = self.descricao_var.get()
        data_inicio = self.data_inicio_var.get()
        data_fim = self.data_fim_var.get()
        status = self.status_var.get()

        try:
            # Converter as strings de data para objetos datetime
            data_inicio = datetime.strptime(data_inicio, "%d/%m/%Y").date()
            data_fim = datetime.strptime(data_fim, "%d/%m/%Y").date()

            if descricao and data_inicio and data_fim:
                tarefa = Tarefa(descricao, data_inicio, data_fim, status)
                self.tarefas.append(tarefa)

                # Adicionar tarefa ao banco de dados
                cursor = self.conn.cursor()
                cursor.execute("INSERT INTO tarefas (descricao, data_inicio, data_fim, status) VALUES (?, ?, ?, ?)",
                               (descricao, data_inicio, data_fim, status))
                self.conn.commit()

                messagebox.showinfo("Sucesso", "Tarefa adicionada com sucesso!")
                self.limpar_campos()
            else:
                messagebox.showerror("Erro", "Preencha todos os campos!")

        except ValueError:
            messagebox.showerror("Erro", "Formato de data inválido. Utilize o formato dd/mm/aaaa.")

    def exibir_lista_tarefas(self):
        lista_tarefas_window = tk.Toplevel(self.root)
        lista_tarefas_window.title("Lista de Tarefas")

        # Criar uma árvore para exibir a lista de tarefas
        tree = ttk.Treeview(lista_tarefas_window, columns=("Descrição", "Data de Início", "Data de Fim", "Status"), show="headings")

        tree.heading("Descrição", text="Descrição")
        tree.heading("Data de Início", text="Data de Início")
        tree.heading("Data de Fim", text="Data de Fim")
        tree.heading("Status", text="Status")

        for tarefa in self.tarefas:
            tree.insert("", "end", values=(tarefa.descricao, tarefa.data_inicio.strftime("%d/%m/%Y"), tarefa.data_fim.strftime("%d/%m/%Y"), tarefa.status))

        tree.pack()

        # Adicionar botões para remover e alterar status
        btn_remover = tk.Button(lista_tarefas_window, text="Remover Tarefa", command=lambda: self.remover_tarefa_selecionada(tree))
        btn_alterar_status_em_andamento = tk.Button(lista_tarefas_window, text="Alterar para Em Andamento",
                                                    command=lambda: self.alterar_status_tarefa(tree, "Em Andamento"))
        btn_alterar_status_concluida = tk.Button(lista_tarefas_window, text="Alterar para Concluída",
                                                 command=lambda: self.alterar_status_tarefa(tree, "Concluído"))

        btn_remover.pack(pady=10)
        btn_alterar_status_em_andamento.pack(pady=10)
        btn_alterar_status_concluida.pack(pady=10)

    def remover_tarefa_selecionada(self, tree):
        selected_item = tree.selection()
        if selected_item:
            descricao = tree.item(selected_item, "values")[0]

            # Remover tarefa da lista e do banco de dados
            for tarefa in self.tarefas:
                if tarefa.descricao == descricao:
                    self.tarefas.remove(tarefa)

                    # Remover tarefa do banco de dados
                    cursor = self.conn.cursor()
                    cursor.execute("DELETE FROM tarefas WHERE descricao=?", (tarefa.descricao,))
                    self.conn.commit()

                    messagebox.showinfo("Sucesso", "Tarefa removida com sucesso!")
                    tree.delete(selected_item)
                    break
        else:
            messagebox.showwarning("Aviso", "Selecione uma tarefa para remover.")

    def alterar_status_tarefa(self, tree, novo_status):
        selected_item = tree.selection()
        if selected_item:
            descricao = tree.item(selected_item, "values")[0]

            # Encontrar a tarefa na lista
            for tarefa in self.tarefas:
                if tarefa.descricao == descricao:
                    # Alterar o status da tarefa
                    tarefa.status = novo_status

                    # Atualizar o banco de dados
                    cursor = self.conn.cursor()
                    cursor.execute("UPDATE tarefas SET status=? WHERE descricao=?", (novo_status, descricao))
                    self.conn.commit()

                    # Atualizar a árvore
                    tree.item(selected_item, values=(tarefa.descricao, tarefa.data_inicio.strftime("%d/%m/%Y"), tarefa.data_fim.strftime("%d/%m/%Y"), tarefa.status))

                    messagebox.showinfo("Sucesso", f"Status da tarefa '{descricao}' alterado para '{novo_status}'.")
                    break
        else:
            messagebox.showwarning("Aviso", "Selecione uma tarefa para alterar o status.")

    def remover_tarefas_concluidas(self):
        # Remover tarefas concluídas da lista e do banco de dados
        tarefas_concluidas = [tarefa for tarefa in self.tarefas if tarefa.status == "Concluído"]

        if tarefas_concluidas:
            for tarefa in tarefas_concluidas:
                self.tarefas.remove(tarefa)

                # Remover tarefa do banco de dados
                cursor = self.conn.cursor()
                cursor.execute("DELETE FROM tarefas WHERE descricao=?", (tarefa.descricao,))
                self.conn.commit()

            messagebox.showinfo("Sucesso", "Tarefas concluídas removidas com sucesso!")
        else:
            messagebox.showinfo("Remover Tarefas Concluídas", "Não há tarefas concluídas para remover.")

    def limpar_campos(self):
        self.descricao_var.set("")
        self.data_inicio_var.set("")
        self.data_fim_var.set("")
        self.status_var.set("A Fazer")

    def __del__(self):
        # Fechar a conexão com o banco de dados ao fechar o aplicativo
        self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = ListaDeTarefasApp(root)
    root.mainloop()
