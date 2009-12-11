Instalacao:
=======

Basico:
-----------------

   GCC, G++, make... (buildessentials), python, python-dev (python-all-dev, parece servir) e python-pycurl

LIBS: 
-----------

   - LIBSVM
        http://www.csie.ntu.edu.tw/~cjlin/libsvm/ (http://www.csie.ntu.edu.tw/~cjlin/cgi-bin/libsvm.cgi?+http://www.csie.ntu.edu.tw/~cjlin/libsvm+zip)
        1) Descompacta libsvm+zip
	2) Ir na pasta /python
	3) make
	4) python setup.py install
   - Tornado Web Server 
	http://www.tornadoweb.org/ (http://www.tornadoweb.org/static/tornado-0.2.tar.gz)
	1) tar xvzf tornado-0.2.tar.gz
	2) cd tornado-0.2
	3) python setup.py build
	4) sudo python setup.py install
   - Beautiful Soup
        http://www.crummy.com/software/BeautifulSoup/ Versão 3.0.7a - não é a mais recente 
	(http://www.crummy.com/software/BeautifulSoup/download/3.x/BeautifulSoup-3.0.7a.tar.gz)
	A versão mais recente deu problemas por isso estamos usando uma mais antiga (dica no próprio site)
	1) Descompactar
	2) sudo python setup.py install	
    - NLTK
	http://www.nltk.org/download (http://nltk.googlecode.com/files/nltk-2.0b6.zip)
	1) Descompactar
	2) sudo python setup.py install
	Tem também via .deb (http://nltk.googlecode.com/files/nltk_2.0b5-1_all.deb). Mas não testei

Rodando o coletor:
==========

1) Preparacão:

   O coletor espera 2 arquivos: layer0.txt e seeds.txt, coloque-os na mesma pasta do resto das classes. É possível passar o path dos arquivos como parâmetro para o HTTPServer.py na ordem layer0.txt seeds.txt, não precisando ser esses nomes.
	
2) Rodando:
   1) python HTTPServer.py (inicia o servidor)
	1.1) Ele vai construir o grafo de contexto com base nas urls dadas no arquivo layer0.txt
	1.2) Senta, por que vai demorar (a coleta de páginas é feita por um único coletor =\, temos que mudar isso)
	1.3) Quando terminar ele vai mostrar uma mensagem, nessa hora inicia-se os coletores
   2) python Fetcher.py (inicia 1 coletor, pode-se iniciar N coletores, mas não exagere)

