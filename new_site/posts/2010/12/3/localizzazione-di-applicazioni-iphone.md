<!--
.. title: Localizzazione di applicazioni Iphone
.. slug: localizzazione-di-applicazioni-iphone
.. date: 2010-12-03 00:00:00
.. tags: 
.. category: 
.. link: 
.. description: 
.. type: text
-->

Nello scrivere una applicazione che cerchi di essere completa ci si deve porre il problema di renderla accessibile anche ad utenti provenienti da paesi in cui l'idioma sia diverso dal proprio. Nella storia del software ci sono state varie modalità di affrontare questo problema in modo più o meno di successo, vediamo come fare con una applicazione in ambiente Mac OSX.

Il problema con il gestire la localizzazione in applicazioni Cocoa deriva dalla loro stessa forza, cioé l'IDE della Apple: **XCode** è sicuramente un ambiente di sviluppo cool ma dimentica le potenzialità insite nella shell Unix di cui si fa discendente il Mac OSX stesso. I file ``.xib``, cioé la descrizione tramite ``XML`` dell'interfaccia dell'applicazione contiene delle stringhe ovviamente scritte in una lingua unica e per modificarle si necessiterebbe di aprire ''interface builder'' ma come processo è lungo e soggetto ad errori, tuttavia esiste un modo più automatica tramite il tool da linea di comando chiamato ``ibtool(1)``. L'unico problema è che l'output, cioé i file ``.strings`` sono in ``UTF-16``, formato con cui è impossibile utilizzare i tools da linea di comando come ``grep(1)`` e ``awk(1)``. Senza tenere conto che a causa del formato del file di configurazione di XCode non è banale automatizzare il processo di creazione dei file di localizzazione che quindi vanno ricreati a mano tramite l'interfaccia.

Per ovviare a questo ho scritto il seguente script di shell che permette di generare/caricare i file con le sole stringhe presenti nelle interfacce; il loro utilizzo è il seguente: prima di tutto bisogna creare tramite l'interfaccia di XCode tutte le localizzazioni dei vari files, questo andrà a creare nella directory contenente il progetto una o più directory nominate ``CC.lproj`` (``CC`` sta ad indicare il **country code**). Per esempio per creare i vari files ``.strings`` per la localizzazione olandese eseguiamo il seguente comando (attenzione che potrebbero essercene più di una di queste directory)

.. code-block:: text

 $ ./localization generate nl.proj/

Una volta editati i file è possibile caricarli nelle interfacce tramite il seguente comando

.. code-block:: text

 $ ./localization install nl.proj/

Per editare i files, consiglio di utilizzare Vim e crearsi delle macro che vadano a sostituire in automatico dalla dashboard di sistema le stringhe da copiare.

Per i posteri, ecco lo script che mi ha salvato molte ore di lavoro:

.. code-block:: bash

 # Copyleft (c) Gianluca Pacchiella <gianluca.pacchiella@ktln2.org>

 usage() {
        cat <<END
 usage: $(basename $0) [list | generate | install] <country code>.lproj

 commands:
	list			elenca le directory per il determinato CC
	generate		crea i file .strings a partire dai .xibs
	install			a partire dai .strings aggiorna i .xibs

 options:

        country code:           il codice di due lettere della localizzazione
 END
 }

  if [ $# -lt 2 ]
 then
        usage
        exit 1
 fi

 COMMAND=$1
 CC_LPROJ_DIR=$2

 # controlliamo che non ci siano comandi estranei
 if [[ $COMMAND != "generate" && $COMMAND != "install" && $COMMAND != "list" ]]
 then
	usage
	exit 1
 fi

 # controlla che esista una directory per questa localizzazione
 # in caso non esista esce per evitare un errore nella digitazione
 if [ ! -d ${CC_LPROJ_DIR} ]
 then
        echo "la directory "${CC_LPROJ_DIR}" non esiste, creala!"
        exit 1
 fi

 # prima genera i file da utilizzare (.strings)
 do_generate() {
	for i in $(ls ${CC_LPROJ_DIR}/*.xib)
	do
		XIB_BASE_FILE=$(basename $i ".xib")
		XIB_SRC_FILE=${CC_LPROJ_DIR}/${XIB_BASE_FILE}.xib
		XIB_DST_FILE=${CC_LPROJ_DIR}/${XIB_BASE_FILE}.strings

		if [ -f ${XIB_DST_FILE} ]
		then
			echo "file "${XIB_DST_FILE}" esiste già"
			exit 1
		fi

		ibtool --generate-strings ${XIB_DST_FILE} ${XIB_SRC_FILE}
	done
 }

 # carica i file .strings dentro i corrispettivi .xib
 do_install() {
	for i in $(ls ${CC_LPROJ_DIR}/*.strings)
	do
		BASENAME=$(basename $i ".strings")
		# l'ultimo argomento dovrebbe essere quello originale ma metto
		# lo stesso
		ibtool --strings-file $i \
			--write ${CC_LPROJ_DIR}/${BASENAME}.xib \
			${CC_LPROJ_DIR}/${BASENAME}.xib
	done
 }

 do_list() {
	find . -iname ${CC_LPROJ_DIR} -type d
 }

 # exec il comando prescelto
 do_"${COMMAND}"

LINKOGRAFIA
-----------

  * http://www.bdunagan.com/2009/03/15/ibtool-localization-made-easy/
  * http://www.bdunagan.com/2009/04/15/ibtool-localization-made-easier/