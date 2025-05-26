#!/bin/bash

# Este script analisa o arquivo de log do squid (access.log) e o combina com
# o arquivo de log do SmbGate (smbgate.log), para gerar um novo arquivo de log,
# semelhante ao access.log, mas que possui, na sua oitava coluna, o nome do
# usuario que acessou determinado conteudo (informacao esta, que nao esta
# presente no arquivo access.log).
#
# REQUIRES
#    - O arquivo access.log preenchido e com permissao de leitura.
#    - O arquivo smbgate.log preenchido e com permissao de leitura.
#    - Um diretorio com permissao de escrita, onde se possa criar o arquivo de
# log.
#
# RETURNS
#    Retorna um arquivo de log, semelhante ao access.log, mas com o nome do
# usuario usuario que acessou determinado conteudo.
#
# AUTHOR: Joe Lopes <lopes.id>
# DATE: 2006-09
##


getFileLine () {
  # DESCRIPTION
  #    Obtem uma determinada linha de um arquivo especificado.
  #
  # REQUIRES
  #    $1 : O caminho do arquivo.
  #    $2 : O numero da linha requerida.
  #    $3 : Armazenara o retorno da funcao.
  #
  # RETURNS
  #    Retorna em $3 a linha requerida.
  fl="$1"
  no="$2"

  eval "$3=`awk `NR=="$no" {print $0}` $file`"
}

getIPAC () {
  # DESCRIPTION
  #    Obtem o endereco IP numa linha de registro do arquivo access.log.
  #
  # REQUIRES
  #    $1 : A linha em questao.
  #    $2 : Variavel de retorno.
  #
  # RETURNS
  #    Retorna em $2 o IP referente a linha $1.
  reg="$1"

  eval "$2=`echo $reg | awk `{print $3}``"
}

getTimeAC () {
  # DESCRIPTION
  #    Obtem o tempo numa linha de registro do arquivo access.log.
  #
  # REQUIRES
  #    $1 : A linha em questao.
  #    $2 : Variavel de retorno.
  #
  # RETURNS
  #    Retorna em $2 o tempo referente a linha $1.
  reg="$1"

  eval "$2=`echo $reg | awk `{print $1}``"
}

getActionSG () {
  # DESCRIPTION
  #    Obtem a acao numa linha de registro do arquivo smbgate.log.
  #
  # REQUIRES
  #    $1 : A linha em questao.
  #    $2 : Variavel de retorno.
  #
  # RETURNS
  #    Retorna em $2 a acao referente a linha $1.
  reg="$1"

  eval "$2=`echo $reg | awk `{print $1}``"
}

getIPSG () {
  # DESCRIPTION
  #    Obtem o endereco IP numa linha de registro do arquivo smbgate.log.
  #
  # REQUIRES
  #    $1 : A linha em questao.
  #    $2 : Variavel de retorno.
  #
  # RETURNS
  #    Retorna em $2 o IP referente a linha $1.
  reg="$1"

  eval "$2=`echo $reg | awk `{print $2}``"
}

getTimeSG () {
  # DESCRIPTION
  #    Obtem o tempo numa linha de registro do arquivo smbgate.log.
  #
  # REQUIRES
  #    $1 : A linha em questao.
  #    $2 : Variavel de retorno.
  #
  # RETURNS
  #    Retorna em $2 o tempo referente a linha $1.
  reg="$1"

  eval "$2=`echo $reg | awk `{print $3}``"
}

getIPSG () {
  # DESCRIPTION
  #    Obtem o nome de usuario numa linha de registro do arquivo smbgate.log.
  #
  # REQUIRES
  #    $1 : A linha em questao.
  #    $2 : Variavel de retorno.
  #
  # RETURNS
  #    Retorna em $2 o nome de usuario referente a linha $1.
  reg="$1"

  eval "$2=`echo $reg | awk `{print $4}``"
}

genLogEntry () {
  # DESCRIPTION
  #    Gera uma linha de entrada para o arquivo de log, resultante da execucao
  # deste script.
  #
  # REQUIRES
  #    $1 : A linha de entrada do arquivo access.log, na qual a entrada sera
  # baseada.
  #    $2 : O nome de usuario, que sera inserido na linha do access.log.
  #    $3 : Variavel de retorno.
  #
  # RETURNS
  #    Retorna em $3 a linha de entrada, obtida atraves de $1 e $2.
  reg="$1"
  usr="$2"

  eval "$3=`echo $reg | awk `{print $1 " " $2 " " $3 " " $4 " " $5 " " $6 " " $7 " " "$usr" " " $9 " " $10 " "}``"
}




createLogFile () {
  # DESCRIPTION
  #    Cria um arquivo texto em branco, para receber os logs.
  #
  # REQUIRES
  #    $1 : O Caminho do diretorio onde o arquivo sera gravado.
  #    $2 : O nome do arquivo de log.
  #    $3 : Caso seja informado o valor "y",  ativa o modo verbose.
  #
  # RETURNS
  #    0 : Arquivo criado com sucesso.
  #    1 : Diretorio inexistente.
  #    2 : Diretorio nao possui permissao de escrita.
  #    3 : Arquivo ja existe.
  #    4 : Arquivo nao pode ser sobreescrito.
  if [ -d "$1" ]; then
    if [ -w "$1" ]; then
        if [ ! -f "$1"/"$2" ]; then
          if [ "$3" = "y" ]; then
              echo -n "Substituir arquivo $1/$2? [y/n] "
              read CHOICE

              if [[ "$CHOICE" = "y" || "$CHOICE" = "Y" ]]; then
                touch "$1"/"$2";
                return 0
              else
                return 3
              fi
          else
              touch "$1"/"$2"
              return 0
          fi
        else
          return 4
        fi
    else
        return 2
    fi
  else
    return 1
  fi
}

exitError () {
  # DESCRIPTION
  #    Exibe uma mensagem de erro e finaliza o script.
  #
  # REQUIRES
  #    $1 : A mensagem de erro.
  #    $2 : O codigo de erro, para o script retornar.
  #
  # RETURNS
  #    Retorna para o sistema operacional o codigo passado em $2.
  echo "$1"
  exit $2
}


##
# MAIN
# O caminho completo do arquivo de log do squid.
fileAC="/var/log/squid/access.log"
# O caminho completo do arquivo de log do Smbgate.
fileSG="/var/run/smbgate/smbgate.log"

lofFileDir="/tmp"        # O diretorio onde ficara o arquivo de log.
logFileName="sg2ac.log"  # O nome do arquivo de log.
verbose="n"              # Modo verbose sim (y) ou nao (n).

# Verificando se os arquivos de log do Squid e do Smbgate existem e se possuem
#    permissao de leitura.
if [[ ! -f $fileAC || ! -r $fileAC || ! -f $fileSG || ! -r $fileSG ]]; then
   exitError "Um dos arquivos de log não existe ou não possui permissão de leitura." 1
fi

# Verificacao de parametros.
# O usuario pode passar como parametros:
#    - o diretorio onde ficara o arquivo de log;
#    - o nome do arquivo de log;
#    - a flag indicando o modo verbose.
# Sao aceitas quaisquer ordens de chamada para os parametros.
case $# in
   1 2 3)
      # Variaveis auxiliares para saber se seus campos de referencia ja foram
      #    passados.
      dir="n" # logFileDir
      fil="n" # logFileName
      ver="n" # verbose

      # Analisa todos os tres parametros passados,
      for i in $@; do
         if [[ -f "$i" && "$fil" = "n" ]]; then
            fil="y"
            logFileName="$i"

         elif [[ -d "$i" && "$dir" = "n" ]]; then
            dir="y"
            logFileDir="$i"

         elif [[ "$i" = "-v" && "ver" = "n" ]]; then
            ver="y"
            verbose="y"

         else
            exitError "Uso: ./smbgate2squid [-v] [LogFile_Dir] [LogFile_Name]" 1
         fi
      done
   ;;

   *)
      exitError "Uso: ./smbgate2squid [-v] [LogFile_Dir] [LogFile_Name]" 1
   ;;
esac

# Cria o arquivo de log.
createLogFile $logFileDir $logFileName $verbose


## logs

# Obtendo a quantidade de linhas dos arquivos de log do Squid e do Smbgate.
totalLinesAC=`wc -l $fileAC`
totalLinesSG=`wc -l $fileSG`


# Varre o arquivo $fileAC completamente.
for (( lineAC=1; lineAC <= totalLinesAC; ++lineAC )); do
   getFileLine $fileAC $lineAC $regAC # Obtem a linha atual
   getIPAC $regAC $ipAC # Obtem o IP da linha atual
   getTimeAC $regAC $timeAC # Obtem o tempo da linha atual

   # Varre o arquivo $fileSG procurando pelo LOGON do usuario.
   for (( lineSG=1;lineSG<=totalLinesSG;++lineSG )); do
      getFileLine $fileSG $lineSG $regSG # Obtem a linha atual
      getActionSG $regSG $actionSG # Obtem a acao da linha atual

      # Somente o LOGON interessa.
      if [ $actionSG = "LOGON" ]; then
         getIPSG $regSG $ipSG # Obtem o IP da linha atual

         # Somente o IP igual ao obtido no arquivo $fileAC interessa.
         if [ $ipSG = $ipAC ]; then
            getTimeSG $regSG $startTimeSG # Obtem o tempo de logon
            getUsernameSG $fileSG $usernameSG # Obtem o nome de usuario

            # Verifica se o tempo esta dentro do limite inferior.
            if [ $startTimeSG <= $timeAC ]; then
               # Procurando o LOGOFF ou FORCADO no restante do arquivo.
               for (( lineSGAux=lineSG+1;lineSGAux<=totalLinesSG;++lineSGAux ))
               do
                  getFileLine $fileSG $lineSGAux $regSG # Obtem a linha atual
                  getActionSG $regSG $actionSG # Obtem a acao atual

                  # Somente LOGOFF interessa.
                  if [ $actionSG = "LOGOFF" ]; then
                     # Obtem o nome de usuario
                     getUsernameSG $regSG $usernameSGAux

                     # Verifica se os nomes de usuarios obtidos no arquivo
                     #    $fileSG coincidem.
                     if [ $usernameSG = $usernameSGAux ]; then
                        getTimeSG $regSG $finishTimeSG # Obtem o tempo do logoff

                        # Verifica se o tempo do usuario logado equivale ao tempo
                        #    obtido no arquivo $fileAC
                        if [[ $timeAC >= $startTimeSG &&
                        $timeAC <= finishTimeSG ]]; then
                           # Gera a entrada.
                           genLogEntry $regAC $usernameSG $logEntry
                           # Grava a entrada no arquivo $logFile.
                           echo $logEntry >> $logFile

                           # Implementacao de uma cache, para agilizar o processo
                           #   de geracao de logs. Entradas contiguas para o
                           #   mesmo IP no arquivo $fileAC sao cadastradas aqui.
                           for ((lineAC=lineAC+1;lineAC<=totalLinesAC;++lineAC ))
                           do
                              getFileLine $fileAC $lineAC $regAC
                              getIPAC $regAC $ipAC

                              if [ $ipAC = $ipSG ]; then
                                 genLogEntry $regAC $usernameSG $logEntry
                                 echo $logEntry >> $logFile
                              else
                                 ((--lineAC)) # Faz a releitura da ultima linha

                                 # Sai dos loops, retornando ao loop
                                 #    que varre o arquivo $fileAC.
                                 break
                                 lineSGAux=totalLinesSG
                                 lineSG=totalLinesSG
                              fi
                           done
                        fi
                     fi
                  fi
               done
            fi
         fi
      fi
   done
done
