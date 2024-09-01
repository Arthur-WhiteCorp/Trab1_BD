import tkinter as tk
from tkinter import ttk

selected_IdProduto = None

def consultar():
    opcao_selecionada = dropdown.get()
    numero_selecionado = inverso_opcoes[opcao_selecionada]  # Obtém o número a partir do texto
    print("Consulta: ", numero_selecionado)
    print("IdProduto: ", selected_IdProduto)

def on_row_selected(event):
    global selected_IdProduto
    selected_item = tree.focus()  # Obtém o item selecionado
    selected_IdProduto = tree.item(selected_item)['values'][1]  # Atualiza o IdProduto associado à linha

def main():
    root = tk.Tk()
    root.title("Tabela com Dropdown, Botão de Consulta e IdProduto")

    # Define o tamanho da janela
    root.geometry("700x400")

    OPCOES_DE_CONSULTA = {
        1: "Dado um produto, listar os 5 comentários mais úteis e com maior avaliação e os 5 comentários mais úteis e com menor avaliação",
        2: "Dado um produto, listar os produtos similares com maiores vendas do que ele",
        3: "Dado um produto, mostrar a evolução diária das médias de avaliação ao longo do intervalo de tempo coberto no arquivo de entrada",
        4: "Listar os 10 produtos líderes de venda em cada grupo de produtos",
        5: "Listar os 10 produtos com a maior média de avaliações úteis positivas por produto",
        6: "Listar a 5 categorias de produto com a maior média de avaliações úteis positivas por produto",
        7: "Listar os 10 clientes que mais fizeram comentários por grupo de produto"
    }

    # Inverso do mapeamento para recuperar o número a partir do texto
    global inverso_opcoes
    inverso_opcoes = {v: k for k, v in OPCOES_DE_CONSULTA.items()}

    global tree
    tree = ttk.Treeview(root)

    # Define as colunas da tabela
    tree['columns'] = ('Nome', 'IdProduto')

    # Define os cabeçalhos das colunas
    tree.column('#0', width=0, stretch=tk.NO)  # Coluna fantasma, não usada
    tree.column('Nome', anchor=tk.W, width=140)
    tree.column('IdProduto', anchor=tk.CENTER, width=100)

    # Cria os cabeçalhos
    tree.heading('#0', text='', anchor=tk.W)
    tree.heading('Nome', text='Nome', anchor=tk.W)
    tree.heading('IdProduto', text='IdProduto', anchor=tk.CENTER)

    # dados da tabela
    data = [
        ('Produto 1', 101),
        ('Produto 2', 102),
        ('Produto 3', 103),
        ('Produto 4', 104),
        ('Produto 5', 105)
    ]

    # Insere os dados na tabela
    for i, (nome, IdProduto) in enumerate(data):
        tree.insert(parent='', index='end', iid=i, text='', values=(nome, IdProduto))

    # Posiciona o Treeview na janela
    tree.pack(side=tk.LEFT, pady=20, padx=20)

    # Adiciona o evento de seleção na tabela
    tree.bind('<<TreeviewSelect>>', on_row_selected)

    # Cria um frame para o dropdown e o botão
    control_frame = tk.Frame(root)
    control_frame.pack(side=tk.LEFT, padx=10, pady=20)

    # Cria o dropdown (Combobox)
    label = tk.Label(control_frame, text="Selecione um número:")
    label.pack(pady=5)

    global dropdown
    dropdown = ttk.Combobox(control_frame, values=list(OPCOES_DE_CONSULTA.values()), width=200)
    dropdown.pack(pady=5)

    # Define o valor padrão do dropdown
    dropdown.current(0)

    # Cria o botão de consulta
    button = ttk.Button(control_frame, text="Consultar", command=consultar)
    button.pack(pady=10)

    global resultado
    resultado = tk.Label(control_frame, text="", font=('Arial', 12))
    resultado.pack(pady=10)

    # Inicia o loop principal
    root.mainloop()

if __name__ == "__main__":
    main()
