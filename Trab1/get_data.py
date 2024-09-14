import re
from enum import Enum

class CategoriesSub:
    def __init__(self, name='', id='', sub: 'CategoriesSub' = None):
        self.name = name
        self.id = id
        self.sub = sub
        
    def __str__(self, level=0):
        return print_category_cascade(self, level)

class Review:
    def __init__(self, total, downloaded, avg_rating):
        self.total = total
        self.downloaded = downloaded
        self.avg_rating = avg_rating
    def __str__(self):
        return f"Total: {self.total}\nDownloaded: {self.downloaded}\nAvgRating: {self.avg_rating}"

class ReviewSub:
    def __init__(self, date='', customer='', rating='', votes='', helpful=''):
        self.date = date
        self.customer = customer
        self.rating = rating
        self.votes = votes
        self.helpful = helpful
        
    def __str__(self):
        return f"\tDate: {self.date}\n\tCustomer: {self.customer}\n\tRating: {self.rating}\n\tVotes: {self.votes}\n\tHelpful: {self.helpful}\n\n"
    
class Similar:
    def __init__(self, total='', ids=[]):
        self.total = total
        self.ids = ids
        
    def __str__(self):
        return f"Total: {self.total}\nIDs: {self.ids}"
class ProductAttributesENUM(Enum):
    ID = 1
    ASIN = 2
    TITLE = 3
    GROUP = 4
    SALESRANK = 5
    SIMILAR = 6
    CATEGORIES = 7
    CATEGORIES_SUB = 8
    REVIEWS = 9
    REVIEWS_SUB = 10

class Product:
    def __init__(self, id='', asin='', title='', group='', salesrank='', similar='', categories='', categories_sub=None, reviews='', reviews_sub=[]):
        if categories_sub is None:
            categories_sub = []
        self.id = id
        self.asin = asin
        self.title = title
        self.group = group
        self.salesrank = salesrank
        self.similar = similar
        self.categories = categories
        self.categories_sub = categories_sub
        self.reviews = reviews
        self.reviews_sub = []
    
    def __str__(self):
        categories_sub_str = str(self.categories_sub) if self.categories_sub else ''
        review_sub_str = "\n".join(str(sub_review) for sub_review in self.reviews_sub)
        return (f"\n\nId: {self.id}\nASIN: {self.asin}\ntitle: {self.title}\n"
                f"group: {self.group}\nsalesrank: {self.salesrank}\nsimilar: {self.similar}\n"
                f"categories: {self.categories}\nCategories-sub:\n{categories_sub_str}\nReviews: {self.reviews}\nReview-sub:\n{review_sub_str}")

def get_line_type(line):
    if line.startswith('Id'):
        return ProductAttributesENUM.ID
    elif line.startswith('ASIN'):
        return ProductAttributesENUM.ASIN
    elif line.startswith('title'):
        return ProductAttributesENUM.TITLE
    elif line.startswith('group'):
        return ProductAttributesENUM.GROUP
    elif line.startswith('salesrank'):
        return ProductAttributesENUM.SALESRANK
    elif line.startswith('similar'):
        return ProductAttributesENUM.SIMILAR
    elif line.startswith('categories'):
        return ProductAttributesENUM.CATEGORIES
    elif line.startswith('|'):
        return ProductAttributesENUM.CATEGORIES_SUB
    elif line.startswith('reviews'):
        return ProductAttributesENUM.REVIEWS
    elif re.match(r'^\d{4}-\d{1,2}-\d{1,2}', line):
        return ProductAttributesENUM.REVIEWS_SUB
    return None

def get_simple_parameter(line, index):
    return line[index:].strip()

def get_parameter_for_similar_atribute(line, index):
    parameters = line[index:].split()
    total = int(parameters[0])
    ids = parameters[1:]
    
    new_similar = Similar(total, ids)
    
    return new_similar

def get_parameter_for_reviews_atribute(line, index):
    parameters = line[index:].split()
    total = int(parameters[1])
    downloaded = int(parameters[3])
    avg_rating = float(parameters[6])
    
    new_reviews = Review(total, downloaded, avg_rating)
    
    return new_reviews

def parse_category(category_str):
    match = re.match(r"([\w\s\-\.\,&]+)\[(\d+)\]", category_str)
    
    if match:
        name = match.group(1).strip()  
        id = match.group(2)
        return name, id
    else:
        raise ValueError("Formato inválido para a string")
    
def filter_empty_strings(vetor):
    return [item for item in vetor if item != '']
    
def map_subcategory_obj(parameters, new_category):
    if len(parameters) > 0:
        name, id = parse_category(parameters[0])
        
        # Criar nova subcategoria se não existir
        if new_category is None:
            new_category = CategoriesSub(name=name, id=id)
        else:
            new_category.name = name
            new_category.id = id
        
        # Recursivamente mapear as subcategorias
        new_category.sub = map_subcategory_obj(parameters[1:], new_category.sub)
        
    return new_category  # Retorna o objeto CategoriesSub atualizado

def print_category_cascade(category, level=0, result=''):
    if category is None:
        return ''
    
    indent = '\t' * level
    
    result += f"{indent}Name: {category.name}, ID: {category.id}\n"
    
    if category.sub:
        result += print_category_cascade(category.sub, level + 1)
    
    return result


def get_parameter_for_subcategories_atribute(line):
    
    parameters = line.split('|')
    parameters = filter_empty_strings(parameters)
    
    new_category = CategoriesSub()
    
    new_category = map_subcategory_obj(parameters, new_category)
    
    return new_category

def get_sub_review(line):
    
    new_sub_review = ReviewSub()
    parameters = line.split()
    
    new_sub_review.date = parameters[0]
    new_sub_review.customer = parameters[2]
    new_sub_review.rating = parameters[4]
    new_sub_review.votes = parameters[6]
    new_sub_review.helpful = parameters[8]
    
    return new_sub_review    
    
lista_produtos = []

with open('amazon-meta.txt', 'r') as file:
    lines = file.readlines()
    new_product = Product()
    
    for line in lines:
        line = line.strip()
        if line:
            line_type = get_line_type(line)
            if line_type == ProductAttributesENUM.ID:
                if new_product.id:
                    lista_produtos.append(new_product)
                new_product = Product()
                new_product.id = get_simple_parameter(line, 3)
            elif line_type == ProductAttributesENUM.ASIN:
                new_product.asin = get_simple_parameter(line, 5)
            elif line_type == ProductAttributesENUM.TITLE:
                new_product.title = get_simple_parameter(line, 6)
            elif line_type == ProductAttributesENUM.GROUP:
                new_product.group = get_simple_parameter(line, 6)
            elif line_type == ProductAttributesENUM.SALESRANK:
                new_product.salesrank = get_simple_parameter(line, 10)
            elif line_type == ProductAttributesENUM.SIMILAR:
                new_product.similar = get_parameter_for_similar_atribute(line, 8)
            elif line_type == ProductAttributesENUM.CATEGORIES:
                new_product.categories = get_simple_parameter(line, 11)
            elif line_type == ProductAttributesENUM.CATEGORIES_SUB:
                new_product.categories_sub.append(get_parameter_for_subcategories_atribute(line))
            elif line_type == ProductAttributesENUM.REVIEWS:
                new_product.reviews = get_parameter_for_reviews_atribute(line, 8)
            elif line_type == ProductAttributesENUM.REVIEWS_SUB:
                new_product.reviews_sub.append(get_sub_review(line))
    
    if new_product.id:
        lista_produtos.append(new_product)


def print_product_details(product):
    # Verifica se o produto é válido
    if not isinstance(product, Product):
        raise ValueError("O argumento deve ser um objeto da classe Product")

    # Inicializa a string de resultado
    result = f"Produto ID: {product.id}\n"
    result += f"ASIN: {product.asin}\n"
    result += f"Title: {product.title}\n"
    result += f"Group: {product.group}\n"
    result += f"Salesrank: {product.salesrank}\n"
    result += f"Similar: {product.similar}\n"
    result += f"Categories: {product.categories}\n"
    
    # Adiciona as subcategorias
    result += "Categories-Sub:\n"
    
    for item in product.categories_sub:
        result += print_category_cascade(item)
    
    # result += print_category_cascade(product.categories_sub) if product.categories_sub else "Nenhuma subcategoria\n"
    
    # Adiciona a revisão
    result += f"Reviews: {product.reviews}\n"
    
    # Adiciona as sub-revisões
    result += "Review-Sub:\n"
    if product.reviews_sub:
        for sub_review in product.reviews_sub:
            result += str(sub_review)
    else:
        result += "Nenhuma sub-revisão\n"
    
    return result

# Exemplo de uso
for item in lista_produtos:
    print(print_product_details(item))

# for item in lista_produtos:
#     print(item)
