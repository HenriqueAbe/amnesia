DROP DATABASE IF EXISTS amnesia;
CREATE DATABASE amnesia;
USE amnesia;

CREATE TABLE Perfil (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    Nome_Usuario VARCHAR(50) UNIQUE NOT NULL,
    Email VARCHAR(100) UNIQUE NOT NULL,
    Senha VARCHAR(255) NOT NULL,
    Tipo ENUM('USER', 'ADMIN') DEFAULT 'USER',
    Data_Cadastro DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Diretor (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    Nome VARCHAR(100) NOT NULL,
    Data_Nascimento DATE,
    Nacionalidade VARCHAR(50)
);

CREATE TABLE Ator_Atriz (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    Nome VARCHAR(100) NOT NULL,
    Data_Nascimento DATE,
    Nacionalidade VARCHAR(50)
);

CREATE TABLE Genero (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    Nome VARCHAR(50) NOT NULL UNIQUE
);



CREATE TABLE Filme (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    Titulo VARCHAR(150) NOT NULL,
    Sinopse TEXT,
    Ano_Lancamento INT,
    Classificacao VARCHAR(10),
    Capa_URL VARCHAR(255),
    Diretor_ID INT,
    AdicionadoPor_ID INT, 
    
    FOREIGN KEY (Diretor_ID) REFERENCES Diretor(ID) ON DELETE SET NULL,
    FOREIGN KEY (AdicionadoPor_ID) REFERENCES Perfil(ID) ON DELETE SET NULL
);


CREATE TABLE Filme_Ator (
    Filme_ID INT,
    Ator_ID INT,
    PRIMARY KEY (Filme_ID, Ator_ID),
    FOREIGN KEY (Filme_ID) REFERENCES Filme(ID) ON DELETE CASCADE,
    FOREIGN KEY (Ator_ID) REFERENCES Ator_Atriz(ID) ON DELETE CASCADE
);

CREATE TABLE Filme_Genero (
    Filme_ID INT,
    Genero_ID INT,
    PRIMARY KEY (Filme_ID, Genero_ID),
    FOREIGN KEY (Filme_ID) REFERENCES Filme(ID) ON DELETE CASCADE,
    FOREIGN KEY (Genero_ID) REFERENCES Genero(ID) ON DELETE CASCADE
);

CREATE TABLE Avaliacao (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    Filme_ID INT NOT NULL,
    Perfil_ID INT NOT NULL, 
    Nota DECIMAL(2,1) NOT NULL,
    Comentario TEXT,
    Data_Avaliacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE (Filme_ID, Perfil_ID), 
    
    FOREIGN KEY (Filme_ID) REFERENCES Filme(ID) ON DELETE CASCADE,
    FOREIGN KEY (Perfil_ID) REFERENCES Perfil(ID) ON DELETE CASCADE
);


INSERT INTO Perfil (Nome_Usuario, Email, Senha, Tipo) VALUES
('admin_geral', 'admin@cinema.com', 'pwd123', 'ADMIN'),
('felipe_urbanek', 'felipe@empresa.com', 'pwd123', 'ADMIN'), 
('joao_cine', 'joao@gmail.com', 'pwd123', 'USER'),
('maria_pipoca', 'maria@hotmail.com', 'pwd123', 'USER'),
('carlos_filmes', 'carlos@yahoo.com', 'pwd123', 'USER'),
('ana_critica', 'ana@outlook.com', 'pwd123', 'USER'),
('pedro_maratona', 'pedro@gmail.com', 'pwd123', 'USER'),
('lucas_vlog', 'lucas@gmail.com', 'pwd123', 'USER'),
('bia_cinema', 'bia@hotmail.com', 'pwd123', 'USER'),
('fernando_geek', 'fernando@yahoo.com', 'pwd123', 'USER'),
('camila_tela', 'camila@gmail.com', 'pwd123', 'USER'),
('roberto_retrô', 'roberto@outlook.com', 'pwd123', 'USER'),
('juliana_star', 'juliana@gmail.com', 'pwd123', 'USER'),
('thiago_dev', 'thiago@empresa.com', 'pwd123', 'USER'),
('victor_eba', 'victor@empresa.com', 'pwd123', 'USER'),
('marco_bot', 'marco@empresa.com', 'pwd123', 'USER'),
('jeferson_rpa', 'jeferson@empresa.com', 'pwd123', 'USER'),
('davi_docs', 'davi@empresa.com', 'pwd123', 'USER'),
('rafael_luz', 'rafael@gmail.com', 'pwd123', 'USER'),
('amanda_cine', 'amanda@hotmail.com', 'pwd123', 'USER');


INSERT INTO Diretor (Nome, Data_Nascimento, Nacionalidade) VALUES
('Lana Wachowski', STR_TO_DATE('21/06/1965', '%d/%m/%Y'), 'Estados Unidos'),
('Christopher Nolan', STR_TO_DATE('30/07/1970', '%d/%m/%Y'), 'Reino Unido'),
('Francis Ford Coppola', STR_TO_DATE('07/04/1939', '%d/%m/%Y'), 'Estados Unidos'),
('David Fincher', STR_TO_DATE('28/08/1962', '%d/%m/%Y'), 'Estados Unidos'),
('Quentin Tarantino', STR_TO_DATE('27/03/1963', '%d/%m/%Y'), 'Estados Unidos'),
('Fernando Meirelles', STR_TO_DATE('09/11/1955', '%d/%m/%Y'), 'Brasil'),
('Bong Joon Ho', STR_TO_DATE('14/09/1969', '%d/%m/%Y'), 'Coreia do Sul'),
('Martin Scorsese', STR_TO_DATE('17/11/1942', '%d/%m/%Y'), 'Estados Unidos');

INSERT INTO Ator_Atriz (Nome, Data_Nascimento, Nacionalidade) VALUES
('Keanu Reeves', STR_TO_DATE('02/09/1964', '%d/%m/%Y'), 'Canadá'),
('Matthew McConaughey', STR_TO_DATE('04/11/1969', '%d/%m/%Y'), 'Estados Unidos'),
('Leonardo DiCaprio', STR_TO_DATE('11/11/1974', '%d/%m/%Y'), 'Estados Unidos'),
('Brad Pitt', STR_TO_DATE('18/12/1963', '%d/%m/%Y'), 'Estados Unidos'),
('Alexandre Rodrigues', STR_TO_DATE('21/05/1983', '%d/%m/%Y'), 'Brasil'),
('Song Kang-ho', STR_TO_DATE('17/01/1967', '%d/%m/%Y'), 'Coreia do Sul'),
('Robert De Niro', STR_TO_DATE('17/08/1943', '%d/%m/%Y'), 'Estados Unidos'),
('Scarlett Johansson', STR_TO_DATE('22/11/1984', '%d/%m/%Y'), 'Estados Unidos'),
('Natalie Portman', STR_TO_DATE('09/06/1981', '%d/%m/%Y'), 'Israel'),
('Christian Bale', STR_TO_DATE('30/01/1974', '%d/%m/%Y'), 'Reino Unido');

INSERT INTO Genero (Nome) VALUES
('Ação'), ('Ficção Científica'), ('Drama'), ('Aventura'), 
('Suspense'), ('Crime'), ('Fantasia'), ('Terror');

INSERT INTO Filme (Titulo, Sinopse, Ano_Lancamento, Classificacao, Diretor_ID, AdicionadoPor_ID) VALUES
('Matrix', 'Realidade simulada e rebelião humana.', 1999, '14', 1, 2),
('Interestelar', 'Exploração espacial e relatividade.', 2014, '10', 2, 2),
('O Poderoso Chefão', 'Drama épico sobre a máfia.', 1972, '16', 3, 1),
('A Origem', 'Invasão de sonhos e subconsciente.', 2010, '14', 2, 2),
('Clube da Luta', 'Insônia, anarquia e um clube secreto.', 1999, '18', 4, 2),
('Pulp Fiction', 'Crime e violência em Los Angeles.', 1994, '18', 5, 1),
('Cidade de Deus', 'Violência urbana nas favelas brasileiras.', 2002, '16', 6, 2),
('Parasita', 'Conflito de classes e suspense coreano.', 2019, '16', 7, 1),
('O Irlandês', 'História de um assassino da máfia.', 2019, '16', 8, 1),
('Batman: O Cavaleiro das Trevas', 'O embate entre Batman e o Coringa.', 2008, '12', 2, 2);

INSERT INTO Filme_Ator (Filme_ID, Ator_ID) VALUES
(1, 1), (2, 2), (3, 7), (4, 3), (5, 4), (6, 7), (7, 5), (8, 6), (9, 7), (10, 10);

INSERT INTO Filme_Genero (Filme_ID, Genero_ID) VALUES
(1, 1), (1, 2), (2, 2), (2, 4), (3, 3), (3, 6), (4, 2), (4, 5), (5, 3), 
(6, 6), (7, 3), (7, 6), (8, 3), (8, 5), (9, 3), (9, 6), (10, 1), (10, 5);


INSERT INTO Avaliacao (Filme_ID, Perfil_ID, Nota, Comentario, Data_Avaliacao) VALUES
(1, 3, 5.0, 'Simplesmente o melhor filme de ficção já feito.', STR_TO_DATE('10/01/2026', '%d/%m/%Y')),
(7, 4, 5.0, 'Uma obra de arte brasileira.', STR_TO_DATE('12/01/2026', '%d/%m/%Y')),
(8, 5, 4.5, 'Final surpreendente!', STR_TO_DATE('15/01/2026', '%d/%m/%Y')),
(10, 17, 5.0, 'Melhor vilão do cinema.', STR_TO_DATE('20/01/2026', '%d/%m/%Y')),
(2, 18, 4.0, 'Visual lindo, mas um pouco longo.', STR_TO_DATE('25/01/2026', '%d/%m/%Y'));



SELECT 
    f.Titulo AS 'Filme', 
    p.Nome_Usuario AS 'Usuário', 
    a.Nota, 
    a.Comentario, 
    DATE_FORMAT(a.Data_Avaliacao, '%d/%m/%Y') AS 'Data da Avaliação'
FROM Avaliacao a
JOIN Filme f ON a.Filme_ID = f.ID
JOIN Perfil p ON a.Perfil_ID = p.ID
ORDER BY a.Nota DESC;