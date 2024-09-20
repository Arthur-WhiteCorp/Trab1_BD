from configparser import ConfigParser
import psycopg2
import os
import tkinter as tk
from tkinter import ttk
import importlib.util
from enum import Enum
from functools import partial

data_query = []
option_query = 0

def show_input():
    user_input = entry.get()  # Retrieve the text from the input box
    input_result.config(text=f"ID SELECIONADO: {user_input}")
    return int(user_input)

def consultar(cursor):
    global option_query
    id_produto = show_input()
    opcao_selecionada = dropdown.get()
    numero_selecionado = inverso_opcoes[opcao_selecionada]  # Obtém o número a partir do texto
    option_query = numero_selecionado
    define_tabela()
    faz_consulta(cursor,numero_selecionado, id_produto)
    insere_dados_tabela()


def faz_consulta(cursor,option:int,id_produto:int):
    print("Consulta: ", option)
    print("ID_PRODUTO: ", id_produto)

    match option:
        case 1:
            query_1(cursor,id_produto)
        case 2:
            query_2(cursor,id_produto)  
        case 3:
            query_3(cursor,id_produto)   
        case 4:
            query_4(cursor)
        case 5:
            query_5(cursor)
        case 6:
            None
        case 7:
            None
    

def on_row_selected(event):
    global selected_IdProduto
    selected_item = tree.focus()  # Obtém o item selecionado
    selected_IdProduto = tree.item(selected_item)['values'][1]  # Atualiza o IdProduto associado à linha


def define_tabela():
    global tree
    global option_query
    print("earai",option_query)
    match option_query:
        case 0:
            tree['columns'] = ('Nome', 'IdProduto')
            # Define os cabeçalhos das colunas
            tree.column('#0', width=0, stretch=tk.NO)  # Coluna fantasma, não usada
            tree.column('Nome', anchor=tk.W, width=140)
            tree.column('IdProduto', anchor=tk.CENTER, width=100)
            # Cria os cabeçalhos
            tree.heading('#0', text='', anchor=tk.W)
            tree.heading('Nome', text='Nome', anchor=tk.W)
            tree.heading('IdProduto', text='IdProduto', anchor=tk.CENTER)
        case 1:
            tree['columns'] = ('REVIEW_ID', 'CUSTOMER_ID','REVIEW_RATING','HELPFUL','VOTE')
            # Define os cabeçalhos das colunas
            tree.column('#0', width=0, stretch=tk.NO)  # Coluna fantasma, não usada
            tree.column('REVIEW_ID', anchor=tk.W, width=5)
            tree.column('CUSTOMER_ID', anchor=tk.CENTER, width=5)
            tree.column('REVIEW_RATING', anchor=tk.CENTER, width=5)
            tree.column('HELPFUL', anchor=tk.CENTER, width=5)
            tree.column('VOTE', anchor=tk.CENTER, width=5)

            # Cria os cabeçalhos
            tree.heading('#0', text='', anchor=tk.W)
            tree.heading('REVIEW_ID', text='REVIEW_ID', anchor=tk.W)
            tree.heading('CUSTOMER_ID', text='CUSTOMER_ID', anchor=tk.CENTER)  
            tree.heading('REVIEW_RATING', text='REVIEW_RATING', anchor=tk.W)
            tree.heading('HELPFUL', text='HELPFUL', anchor=tk.W)
            tree.heading('VOTE', text='VOTE', anchor=tk.CENTER)   
            #REVIEW_ID, CUSTOMER_ID, REVIEW_RATING, HELPFUL, VOTE
        case 2:
            None
        case 3:
            None
        case 4:
            None
        case 5:
            None
        case 6:
            None
        case 7: 
            None   

def insere_dados_tabela():
    global option_query
    global data_query

    match option_query:
        case 1:
            i = 0
            for data in data_query:
                tree.insert(parent='', 
                            index='end', 
                            iid=i, text='', 
                            values=(data[0], 
                                    data[1],
                                    data[2],
                                    data[3],
                                    data[4]))
                i = i + 1
        case 2:
            None
        case 3:
            None
        case 4:
            None
        case 5:
            None
        case 6:
            None
        case 7:
            None

def main(cursor):
    root = tk.Tk()
    root.title("Tabela com Dropdown, Botão de Consulta e IdProduto")

    # Define o tamanho da janela
    root.geometry("1260x1200")

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
    
    define_tabela()

    
    # dados da tabela
    global data_query

    # Insere os dados na tabela
    insere_dados_tabela()
    # Posiciona o Treeview na janela
    tree.pack(side=tk.LEFT, pady=20, padx=20)

    # Adiciona o evento de seleção na tabela
    #tree.bind('<<TreeviewSelect>>', on_row_selected)

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
    button = ttk.Button(control_frame, text="Consultar", command=partial(consultar,cursor))
    button.pack(pady=10)

    global resultado
    resultado = tk.Label(control_frame, text="", font=('Arial', 12))
    resultado.pack(pady=10)

    # Label do input
    entry_label = tk.Label(control_frame, text="Ponha o ID do produto:")
    entry_label.pack(pady=0)

    #Input box
    global entry
    entry = tk.Entry(control_frame, width=30)
    entry.pack(pady=0)

    
    

    #SHOW INPUT
    global input_result
    input_result = tk.Label(control_frame, text="")
    input_result.pack(pady=10)

    # Inicia o loop principal
    root.mainloop()




def resolve_path(file_name):
    current_dir_path = os.path.dirname(__file__)
    file_path = f"{current_dir_path}/{file_name}"
    return file_path


def load_config(file_name='database.ini', section='postgresql'):
    parser = ConfigParser()
    file_path = resolve_path(file_name)
    
    parser.read(file_path)

    # get section, default to postgresql
    config = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            config[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, file_path))

    return config



def connect(config):
    """ Connect to the PostgreSQL database server """
    try:
        my_connection = psycopg2.connect(**config)
        print('Connected to the PostgreSQL server.')
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)

    return my_connection

def close_connection(my_connection):
    try:
        my_connection.close()
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)

def create_cursor(my_connection):
    try:
        my_cursor = my_connection.cursor()
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)
    
    return my_cursor

def query_1(cursor,product_id:int):

    # Query para obter os 5 comentários mais úteis e com maior avaliação
    query_high_rating = """
        SELECT REVIEW_ID, CUSTOMER_ID, REVIEW_RATING, HELPFUL, VOTE
        FROM REVIEW
        WHERE PRODUCT_ID = %s
        ORDER BY REVIEW_RATING DESC, HELPFUL DESC
        LIMIT 5;
    """

    # Query para obter os 5 comentários mais úteis e com menor avaliação
    query_low_rating = """
        SELECT REVIEW_ID, CUSTOMER_ID, REVIEW_RATING, HELPFUL, VOTE
        FROM REVIEW
        WHERE PRODUCT_ID = %s
        ORDER BY REVIEW_RATING ASC, HELPFUL DESC
        LIMIT 5;
    """

    # Executar a query para comentários com maior avaliação
    cursor.execute(query_high_rating, (product_id,))
    high_rating_reviews = cursor.fetchall()

    # Executar a query para comentários com menor avaliação
    cursor.execute(query_low_rating, (product_id,))
    low_rating_reviews = cursor.fetchall()

    global data_query

    data_query = high_rating_reviews + low_rating_reviews

    # Exibir os resultados
    print("5 Comentários mais úteis com maior avaliação:")
    for review in high_rating_reviews:
        print(review)

    print("\n5 Comentários mais úteis com menor avaliação:")
    for review in low_rating_reviews:
        print(review)
        
def query_2(cursor,product_id:int):

    # Query para listar os produtos similares com maiores vendas
    query_similar_products = """
        SELECT p_sim.SIMILAR_ASIN, p2.TITLE, p2.SALES_RANK
        FROM PRODUCT p
        JOIN PRODUCT_SIMILAR p_sim ON p.PRODUCT_ID = p_sim.PRODUCT_ID
        JOIN PRODUCT p2 ON p_sim.SIMILAR_ASIN = p2.ASIN
        WHERE p.PRODUCT_ID = %s
        AND p2.SALES_RANK < p.SALES_RANK;
    """

    # Executar a query
    cursor.execute(query_similar_products, (product_id,))
    similar_products = cursor.fetchall()

    global data_query
    data_query = similar_products

    # Exibir os resultados
    print("Produtos similares com maiores vendas:")
    for product in similar_products:
        print(f"ASIN: {product[0]}, Título: {product[1]}, Ranking de Vendas: {product[2]}")

def query_3(cursor,product_id:int):
    query_avg_rating = """ SELECT REVIEW_1.REVIEW_DATE, avg(REVIEW_2.REVIEW_RATING)
                           FROM REVIEW AS REVIEW_1 ,REVIEW AS REVIEW_2
                           WHERE REVIEW_1.REVIEW_DATE >= REVIEW_2.REVIEW_DATE
                           and REVIEW_1.PRODUCT_ID = %s
                           and REVIEW_2.PRODUCT_ID = REVIEW_1.PRODUCT_ID
                           GROUP BY REVIEW_1.REVIEW_DATE
                           ORDER BY REVIEW_1.REVIEW_DATE"""

    cursor.execute(query_avg_rating, (product_id,))
    ratings = cursor.fetchall()
    global data_query
    data_query = ratings


    print("EVOLUÇÃO DAS MÉDIAS:")
    for rating in ratings:
        print(f"DATE: {rating[0]}, RATING_AVG: {rating[1]}")
        
def query_4(cursor):
    my_query = """  
              WITH RankedProducts AS (
              SELECT 
                  ASIN,
                  TITLE,
                  PRODUCT_GROUP,
                  SALES_RANK,
                  ROW_NUMBER() OVER (PARTITION BY PRODUCT_GROUP ORDER BY SALES_RANK) AS rank
              FROM 
                  PRODUCT
      )
      SELECT 
          ASIN,
          TITLE,
          PRODUCT_GROUP,
          SALES_RANK
      FROM 
          RankedProducts
      WHERE 
          rank <= 10
      ORDER BY 
          PRODUCT_GROUP, SALES_RANK"""

    cursor.execute(my_query)
    answers = cursor.fetchall()

    global data_query
    data_query = answers

    print("Resposta:")
    for answer in answers:
        if answer[1] and answer[2] and answer[3]:
            print(answer)
        
def query_5(cursor):
    my_query = """
    SELECT 
    P.TITLE, 
        AVG(R.HELPFUL) AS AVG_HELPFUL
    FROM 
        PRODUCT P
    JOIN 
        REVIEW R ON P.PRODUCT_ID = R.PRODUCT_ID
    WHERE 
        R.REVIEW_RATING > 0  -- Considera apenas reviews com rating maior que zero
    GROUP BY 
        P.TITLE
    HAVING 
        AVG(R.HELPFUL) > 0  -- Garante que só produtos com avaliações úteis sejam considerados
    ORDER BY 
        AVG_HELPFUL DESC
    LIMIT 10;
    """
    cursor.execute(my_query)
    answers = cursor.fetchall()

    global data_query
    data_query = answers

    print("Resposta:")
    for answer in answers:
        print(answer)
        
def query_6(cursor):
    my_query = """
        SELECT 
        P.PRODUCT_GROUP, 
        AVG(R.HELPFUL) AS AVG_HELPFUL
    FROM 
        PRODUCT P
    JOIN 
        REVIEW R ON P.PRODUCT_ID = R.PRODUCT_ID
    WHERE 
        R.REVIEW_RATING >= 1  -- Considera apenas avaliações com rating positivo
    GROUP BY 
        P.PRODUCT_GROUP
    HAVING 
        AVG(R.HELPFUL) > 0  -- Garante que apenas grupos com médias úteis positivas sejam considerados
    ORDER BY 
        AVG_HELPFUL DESC
    LIMIT 5;

    """
    cursor.execute(my_query)
    answers = cursor.fetchall()

    global data_query
    data_query = answers

    print("Resposta:")
    for answer in answers:
        print(answer)
        
def query_7(cursor):
    my_query = """
WITH RankedReviews AS (
    SELECT 
        P.PRODUCT_GROUP, 
        R.CUSTOMER_ID, 
        COUNT(R.REVIEW_ID) AS TOTAL_REVIEWS,
        ROW_NUMBER() OVER (PARTITION BY P.PRODUCT_GROUP ORDER BY COUNT(R.REVIEW_ID) DESC) AS RANK
    FROM 
        PRODUCT P
    JOIN 
        REVIEW R ON P.PRODUCT_ID = R.PRODUCT_ID
    GROUP BY 
        P.PRODUCT_GROUP, 
        R.CUSTOMER_ID
)
SELECT 
    PRODUCT_GROUP, 
    CUSTOMER_ID, 
    TOTAL_REVIEWS
FROM 
    RankedReviews
WHERE 
    RANK <= 10
ORDER BY 
    PRODUCT_GROUP, 
    TOTAL_REVIEWS DESC;

    """
    cursor.execute(my_query)
    answers = cursor.fetchall()

    global data_query
    data_query = answers

    print("Resposta:")
    for answer in answers:
        print(answer)
        
if __name__ == '__main__':

    config = load_config()
    my_connection = connect(config)
    
    my_cursor = create_cursor(my_connection)
    # query_1(my_cursor)
    query_6(my_cursor)
    # main(my_cursor)

    close_connection(my_connection)
