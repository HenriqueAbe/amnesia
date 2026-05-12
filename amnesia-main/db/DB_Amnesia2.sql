DROP DATABASE IF EXISTS amnesia;
CREATE DATABASE amnesia;
USE amnesia;

-- 1. Tabela Usuario (Antiga Perfil)
CREATE TABLE Usuario (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    Nome_Usuario VARCHAR(50) NOT NULL,
    Email VARCHAR(100) UNIQUE NOT NULL,
    Senha VARCHAR(255) NOT NULL,
    Tipo ENUM('USER', 'ADMIN') DEFAULT 'USER',
    Data_Cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
    Foto_Usuario MEDIUMBLOB DEFAULT NULL
);

-- 2. Tabela Diretor
CREATE TABLE Diretor (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    Nome VARCHAR(100) NOT NULL,
    Data_Nascimento DATE,
    Nacionalidade VARCHAR(50)
);

-- 3. Tabela Ator_Atriz
CREATE TABLE Ator_Atriz (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    Nome VARCHAR(100) NOT NULL,
    Data_Nascimento DATE,
    Nacionalidade VARCHAR(50)
);

-- 4. Tabela Genero
CREATE TABLE Genero (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    Nome VARCHAR(50) NOT NULL UNIQUE
);

-- 5. Tabela Filme
CREATE TABLE Filme (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    Titulo VARCHAR(150) NOT NULL,
    Sinopse TEXT,
    Ano_Lancamento INT,
    Classificacao VARCHAR(10),
    Diretor_ID INT,
    AdicionadoPor_ID INT,
    CAPA_URL VARCHAR(2083),
    FOREIGN KEY (Diretor_ID) REFERENCES Diretor(ID) ON DELETE SET NULL,
    FOREIGN KEY (AdicionadoPor_ID) REFERENCES Usuario(ID) ON DELETE SET NULL
);

-- 6. Tabela Filme_Ator (N x N com atributo Personagem)
CREATE TABLE Filme_Ator (
    Filme_ID INT,
    Ator_ID INT,
    Personagem VARCHAR(100) NOT NULL,
    PRIMARY KEY (Filme_ID, Ator_ID),
    FOREIGN KEY (Filme_ID) REFERENCES Filme(ID) ON DELETE CASCADE,
    FOREIGN KEY (Ator_ID) REFERENCES Ator_Atriz(ID) ON DELETE CASCADE
);

-- 7. Tabela Filme_Genero (N x N)
CREATE TABLE Filme_Genero (
    Filme_ID INT,
    Genero_ID INT,
    PRIMARY KEY (Filme_ID, Genero_ID),
    FOREIGN KEY (Filme_ID) REFERENCES Filme(ID) ON DELETE CASCADE,
    FOREIGN KEY (Genero_ID) REFERENCES Genero(ID) ON DELETE CASCADE
);

-- 8. Tabela Lista_Usuario (Nova N x N entre Usuario e Filme)
CREATE TABLE Lista_Usuario (
    Usuario_ID INT,
    Filme_ID INT,
    Data_Adicao DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (Usuario_ID, Filme_ID),
    FOREIGN KEY (Usuario_ID) REFERENCES Usuario(ID) ON DELETE CASCADE,
    FOREIGN KEY (Filme_ID) REFERENCES Filme(ID) ON DELETE CASCADE
);

-- 9. Tabela Avaliacao
CREATE TABLE Avaliacao (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    Filme_ID INT NOT NULL,
    Usuario_ID INT NOT NULL, 
    Nota DECIMAL(2,1) NOT NULL,
    Comentario TEXT,
    Data_Avaliacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (Filme_ID, Usuario_ID), 
    FOREIGN KEY (Filme_ID) REFERENCES Filme(ID) ON DELETE CASCADE,
    FOREIGN KEY (Usuario_ID) REFERENCES Usuario(ID) ON DELETE CASCADE
);

-- INSERÇÃO DE DADOS
INSERT INTO Usuario (Nome_Usuario, Email, Senha, Tipo) VALUES
('admin_geral', 'admin@cinema.com', 'pwd123', 'ADMIN'),
('felipe_urbanek', 'felipe@empresa.com', 'pwd123', 'ADMIN'), 
('joao_cine', 'joao@gmail.com', 'pwd123', 'USER');

INSERT INTO Diretor (Nome, Data_Nascimento, Nacionalidade) VALUES
('Lana Wachowski', '1965-06-21', 'Estados Unidos'),
('Christopher Nolan', '1970-07-30', 'Reino Unido');

INSERT INTO Ator_Atriz (Nome, Data_Nascimento, Nacionalidade) VALUES
('Keanu Reeves', '1964-09-02', 'Canadá'),
('Christian Bale', '1974-01-30', 'Reino Unido');

INSERT INTO Genero (Nome) VALUES ('Ação'), ('Ficção Científica'), ('Drama');

INSERT INTO Filme (Titulo, Sinopse, Ano_Lancamento, Classificacao, Capa_URL, Diretor_ID, AdicionadoPor_ID) VALUES
('Matrix', 'Realidade simulada e rebelião humana.', 1999, '14', 'https://url.com/matrix.jpg', 1, 2),
('Batman: O Cavaleiro das Trevas', 'O embate entre Batman e o Coringa.', 2008, '12', 'https://url.com/batman.jpg', 2, 2);

-- Inserindo com o novo campo Personagem
INSERT INTO Filme_Ator (Filme_ID, Ator_ID, Personagem) VALUES
(1, 1, 'Thomas Anderson / Neo'),
(2, 2, 'Bruce Wayne / Batman');

-- Exemplo de Lista de Favoritos (N x N Usuario/Filme)
INSERT INTO Lista_Usuario (Usuario_ID, Filme_ID) VALUES (3, 1), (3, 2);

-- CONSULTA DE TESTE
SELECT 
    f.Titulo AS 'Filme', 
    u.Nome_Usuario AS 'Adicionado Por',
    aa.Nome AS 'Ator',
    fa.Personagem AS 'Papel'
FROM Filme f
JOIN Usuario u ON f.AdicionadoPor_ID = u.ID
JOIN Filme_Ator fa ON f.ID = fa.Filme_ID
JOIN Ator_Atriz aa ON fa.Ator_ID = aa.ID;