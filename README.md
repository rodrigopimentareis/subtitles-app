#Construir imagem
docker build -t subtitles/subtitles .
#Executar imagem
docker run -p 49160:6001 subtitles/subtitles
#O site vai estar em localhost:49160
