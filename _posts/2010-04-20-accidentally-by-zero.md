---
layout: post
title: 'accidentally by zero'
comments: true
---
Facendo ripetizioni ad un ragazzo del politecnico mi sono ritrovato a dover
risolvere un esercizio relativo ai numeri complessi, cioé trovare il valore di
\\(\ln (-i)^8\\) ; il tutto pare abbastanza straightforward (tenendo
 conto che \\(z=a+ib=\rho e^{i\theta}\\)).

$$
\eqalign{
 \ln\left(-i\right)^8 &= 8\ln \left(-i\right)\cr
 &= 8\left(\ln 1 -i{\pi\over2} \right)\cr
 &= -4i \pi \cr
 }
$$
il problema arriva se uno tenta di risolverlo direttamente calcolando il valore di \\((-i)^8\\)

$$
\eqalign{
 \ln\left(-i\right)^8 &= \ln\left[(-i)^{2\cdot4}\right]\cr
 &= \ln\left[(-1)^4\right]\cr
 &= \ln 1 \cr
 &= 0 \cr
 }
$$
Come è possibile avere due risultati differenti? semplicemente perché
nell'analisi complessa le funzioni non si comportano "bene" come l'analisi
matematica su \\(R\\) ma alcune di esse possono essere polidrome (cioé allo
stesso dominio possono coincidere immagini attraverso la funzione diverse). Nel
caso del logaritmo questo è abbastanza ovvio se consideriamo che un numero (in
questo caso complesso scritto in notazione polare) rimane invariato se
moltiplicato per 1

$$ z\cdot 1 = z\cdot e^{i2\pi}$$

ma non il suo logaritmo

$$\ln z = \ln z + i\,2\pi$$

Questo significa appunto che la funzione logaritmo è *una funzione a molti
valori la cui immagine risiede su una superficie di Riemann ad infiniti fogli*,
quindi i due risultati sono stati calcolati semplicemente su due fogli diversi.
Quindi alla fine, entrambi i valori sono esatti, semplicemente calcolati su
fogli diversi.
