#! /usr/bin/env python
# -*- coding: utf-8 -*-

from tkinter import filedialog
from tkinter import *
from networkx import DiGraph,complement,get_node_attributes,is_directed_acyclic_graph #233MB
from numpy import array,split,column_stack,zeros,delete #155MB
from random import shuffle,randint
from time import time
from math import log,factorial
from graphviz import Digraph
from threading import Thread
from tkinter import font
import os
import copy
from PIL import Image,ImageTk

#os.environ["PATH"] += os.pathsep + 'C:/Program Files (x86)/Graphviz2.38/bin/'

def drawPng(G):
    gr = Digraph('G', format='png',filename='hello.gv')
    for node in G.nodes():
        gr.node(node)
    for (u,v) in G.edges():
        gr.edge(u,v)
    gr.render('Graph_GUI')
    os.remove("Graph_GUI")
    
def tempo(intervallo):
    minuti=int(intervallo/60)
    secondi=round(intervallo,1)-minuti*60
    if minuti>0 or secondi>9:
        secondi=int(secondi)
    stringa=str(minuti)+' min. '+str(secondi)+' sec. '
    return stringa

def randomEdges(Graph):
    G=Graph.copy()
    for (u,v) in copy.deepcopy(G.edges()):
        G.remove_edge(u,v)
    nodes=len(G.nodes())
    comp=list(complement(G).edges())
    e=list(Graph.edges())
    for i in range(randint(3,6)):
        for j in range(randint(2,5)):
            shuffle(comp)
        
    for (u,v) in comp:
        for j in range(randint(2,7)):
            for k in range(randint(2,5)):
                num=randint(1,nodes)
        if num==1:
            G.add_edge(u,v)
            if is_directed_acyclic_graph(G)==False:
                G.remove_edge(u,v)
    if len(G.edges())==0:
        G=randomEdges(G) 
        
    if len(e)!=len(G.edges()):
        return G
    for (u,v) in list(G.edges()):
        if (u,v) not in e:
            return G
    G=randomEdges(G)

class Oggetto():
    configurazione=''
    num_istanze=1
    
#/////////////////////ALCUNE FUNZIONI/////////////
def datasetIndex(node,dataset):#restituisce l'indice del nodo nel dataset
    index_node=0
    while dataset[0][index_node]!=node:
        index_node=index_node+1
    return index_node

def Ri(node,dataset):#restituisce in numero di istanze del nodo nel dataset
    tmp=set()
    index_of_node=datasetIndex(node,dataset)
    for i in range(1,dataset.shape[0]):
        tmp.add(dataset[i][index_of_node])
        
    return len(tmp)

#////////////CALCOLO FORMULA//////////
def Formula(G,node,dataset,Ri,index):
    '''
    Adesso creo un newdataset con solo nodo+padri
    '''
    newdataset=dataset[:,[index[node]]]                                  #aggiungo la colonna relativa al nodo
    for n in G.predecessors(node):
        newdataset=column_stack([newdataset, dataset[:,index[n]]])    #aggiungo le colonne relative ai padri

    '''
    Adesso creo due insiemi!
        Per la prima sommatoria:
        padri = vettore di oggetti che hanno per nome una configurazione dei padri del nodo 
                sottoforma di stringa e il numero di istanze di tale configurazione

        Per la seconda sommatoria:
        padri_e_figlio = vettore di oggetti che hanno per nome una configurazione di padri+figlio
                         sottoforma di stringa e il numero di istanze di tale configurazione
    '''
    padri=[]
    padri_e_figlio=[]

    for i in range(1,newdataset.shape[0]):
        configurazione=''
        for j in range(1,newdataset.shape[1]):
            configurazione=configurazione+newdataset[i][j]           #concateno le righe dei padri
        
        found=0
        for obj in padri:
            if obj.configurazione==configurazione:
                found=1
                obj.num_istanze=obj.num_istanze+1
                break
        if found==0:
            obj=Oggetto()                                      #obj.num_istanze=1
            obj.configurazione=configurazione          
            padri.append(obj)
            
        configurazione=configurazione+newdataset[i][0]         #aggiungo la configurazione del figlio
        
        found=0
        for obj in padri_e_figlio:
            if obj.configurazione==configurazione:
                found=1
                obj.num_istanze=obj.num_istanze+1
                break
        if found==0:
            obj=Oggetto()
            obj.configurazione=configurazione
            padri_e_figlio.append(obj)
            
            
    '''
    Calcolo della prima sommatoria (il fattore (Ri-1) lo porto fuori dalla sommatoria)
    '''
    fattore=log(factorial(Ri-1))*(len(padri))
    
    for obj in padri:
        fattore=fattore-log(factorial(obj.num_istanze+Ri-1))
        
    '''
    Calcolo della seconda sommatoria
    '''
    for obj in padri_e_figlio:
        fattore=fattore+log(factorial(obj.num_istanze))
        
    return -fattore

#/////////////////////////////////////////////////////

    
class MiaApp:
  def __init__(self, genitore):
    self.mioGenitore = genitore  ### (7) ricorda: il genitore e` radice
    self.mioContenitore1 = Frame(genitore)
    self.mioContenitore1.pack(side=LEFT)
    self.buttomaltezza=2
    self.buttomlarghezza=8
    self.font=15
    self.myfont = font.Font(size=13)
    self.iter=0
    self.mioGenitore.title("Learning of the structure of Bayesian networks")
    self.mioGenitore.iconbitmap('ico/graph.ico')
    
    self.menubar = Menu(genitore)
    self.window = Toplevel(root)
    self.window.destroy()
    self.filemenu = Menu(self.menubar, tearoff=0)
    self.filemenu.add_command(label="Importa dataset",command=self.Apri)
    self.filemenu.add_separator()
    self.filemenu.add_command(label="Exit",command=self.mioGenitore.destroy)
    self.menubar.add_cascade(label="File", menu=self.filemenu)
    
    genitore.config(menu=self.menubar)

    self.pulsanteavvio = Label(self.mioContenitore1)
    self.pulsanteavvio.configure(text = "Run",bg='white',font=("Helvetica", 1,'bold'),borderwidth=2, relief="groove")
    self.pulsanteavvio.configure(height = self.buttomaltezza, width = self.buttomlarghezza)
    self.pulsanteavvio.grid(row=0,column=1,sticky=W)  
    self.pulsanteavvio.bind("<Button-1>", self.HC)
    self.avvio=1
    
    self.pulsantestop = Label(self.mioContenitore1)
    self.pulsantestop.configure(text = "Pause",bg='white',font=("Helvetica", self.font))
    self.pulsantestop.config(height = self.buttomaltezza, width = self.buttomlarghezza)
    self.pulsantestop.grid(row=0,column=2,sticky=W)  
    self.pulsantestop.bind("<Button-1>", self.stop)

    self.pulsanteclear = Label(self.mioContenitore1)
    self.pulsanteclear.configure(text = "Restart",bg='white',font=("Helvetica", self.font))
    self.pulsanteclear.config(height = self.buttomaltezza, width = self.buttomlarghezza)
    self.pulsanteclear.grid(row=0,column=3,sticky=W)  
    self.pulsanteclear.bind("<Button-1>", self.clear)
    
    self.pulsantedataset = Label(self.mioContenitore1)
    self.pulsantedataset.configure(text = "Dataset",font=("Helvetica", self.font,'bold'),bg='sky blue',borderwidth=2, relief="groove")
    self.pulsantedataset.config(height = self.buttomaltezza, width = self.buttomlarghezza)
    self.pulsantedataset.grid(row=0,column=4,sticky=W)  
    self.pulsantedataset.bind("<Button-1>", self.showDataset)

    self.pulsanteimmagine = Label(self.mioContenitore1)
    self.pulsanteimmagine.configure(text = "",font=("Helvetica", self.font),borderwidth=2, relief="groove")
    self.pulsanteimmagine.grid(row=0,column=0)
    self.pulsanteimmagine.bind("<Button-1>", self.openImmagine)
    
    self.testo = Label(self.mioContenitore1)
    self.testo.configure(text = "cases:",font=("Helvetica", int(self.font/1.2)))
    self.testo.grid(row=1,column=1,sticky=W)
    
    self.casi=Scale(self.mioContenitore1, from_=5, to=100,orient=HORIZONTAL,length=320)
    self.casi.grid(row=1,column=1,columnspan=4,sticky=E)
    
    self.arcs = Label(self.mioContenitore1)
    self.arcs.configure(text = "edges:",font=("Helvetica", int(self.font/1.2)))
    self.arcs.grid(row=2,column=1,sticky=W)
    
    self.null = Label(self.mioContenitore1)
    self.null.configure(text = "null",bg='white',font=("Helvetica", self.font))
    self.null.config(height = int(self.buttomaltezza/2), width = int(self.buttomlarghezza/2))
    self.null.grid(row=2,column=2,sticky=W)  
    self.null.bind("<Button-1>", self.empty)
    
    self.rand = Label(self.mioContenitore1)
    self.rand.configure(text = "rand",bg='white',font=("Helvetica", self.font))
    self.rand.config(height = int(self.buttomaltezza/2), width = int(self.buttomlarghezza/2))
    self.rand.grid(row=2,column=3,sticky=W)  
    self.rand.bind("<Button-1>", self.randomize)
    
    self.dataset=array(0)
    self.Graph=DiGraph()
    self.Graph_start=DiGraph()
    
    
    self.tmptime=0
    self.time=0
    self.box=Listbox(self.mioContenitore1,font=self.myfont,width=46, height=18)
    self.box.grid(row=0,column=0,columnspan=5,rowspan=3,sticky=W)
    
    self.scrollbar = Scrollbar(self.mioContenitore1)
    self.scrollbar.config(command=self.box.yview)

    self.box.config(yscrollcommand=self.scrollbar.set)
    self.scrollbar.grid_forget()
    
    self.imp = Label(self.mioContenitore1)
    self.imp.configure(text = "Import Dataset",font=("Helvetica", 27),borderwidth=2, relief="groove")
    self.imp.grid(row=0,column=1,columnspan=5,rowspan=3)
    self.imp.bind("<Button-1>", self.im)
      
  def im(self,evento):
      self.Apri()

  def Run(self, evento):
      if self.avvio==1:
          return
      if self.dataset==0:
          self.box.insert(END,'YOU MUST IMPORT DATASET')
          self.box.update()
          return
      if self.iter==0:
          self.box.delete(0, END)
      self.pulsanteavvio.config(text='Running...',bg='white',font=("Helvetica", self.font),borderwidth=0, relief="groove")
      self.pulsantestop.config(bg='red',font=("Helvetica", self.font,'bold'),borderwidth=2, relief="groove")
      self.pulsanteclear.config(bg='white',font=("Helvetica", self.font),borderwidth=0, relief="groove")
      self.pulsanteavvio.update()
      self.box.grid(row=1,column=0,columnspan=5,rowspan=3)
      self.scrollbar.grid(row=1, ipady = 267)
      self.box.config(height=29)
      self.pulsantestop.update()
      self.box.update()
      
      self.avvio=1
      G=self.Graph.copy()
      dataset=split(self.dataset,[0,self.casi.get()+1])
      dataset=dataset[1]
      '''
      Inizzializzaizone. Creo tre insiemi:
          ArrayIndex[u]=indice del nodo "u" nel dataset
          ArrayScore[u]=fattore di score riferito al nodo "u" (data la rete corrente e il dataset)
          ArrayRi[u]=numero di valori che assume il nodo "u" nel dataset
      '''
      self.box.update()
      proporzione= len(complement(G).edges())+len(G.edges())+1
      tmp_score=DiGraph()
      for n in G.nodes():
          self.box.update()
          tmp_score.add_node(n,index=datasetIndex(n,dataset))
          
      ArrayIndex=get_node_attributes(tmp_score,'index')
      self.box.update()
      c=0
      for n in G.nodes():
          c=c+1
          Ri_nodo=Ri(n,dataset)
          if self.avvio==0:
              return
          if self.iter==0:
              self.box.delete(END)
              self.box.insert(END,'Progress: '+str(int(c*100/len(G.nodes())))+'%')
          self.box.see(END)
          self.box.update()
          tmp_score.add_node(n, score=Formula(G,n,dataset,Ri_nodo,ArrayIndex), Ri=Ri_nodo)
          
      ArrayScore=get_node_attributes(tmp_score,'score')
      ArrayRi=get_node_attributes(tmp_score,'Ri')
      self.box.delete(END)
      self.box.update()
      '''
      Ottengo lo score della rete sommando tutti i valori di ArrayScore
      '''
      tmp_score=0
      for n in G.nodes():
          tmp_score=tmp_score + ArrayScore[n]
      string= "score iniziale= "+str(tmp_score)
      self.box.update()
      if self.avvio==0:
              return
      if self.iter==0:
          self.box.insert(END,string)
          self.box.insert(END,' ')
          self.time=0
      else:
          self.iter=self.iter-1
      self.box.update()
      inizio=time()
      self.tmptime=inizio
      self.box.update()
      tipo='tipo di operazione elementare'
      while tipo!='not found':
          self.box.update()
          inizio_iterazione=time()
          tipo='not found'
          self.iter=self.iter+1
          c=0
          self.box.insert(END,'Search: '+str(c)+'%')
          self.box.see(END)
          self.box.update()
          scoreIniziale=tmp_score
          if self.avvio==0:
              return

          for (u,v) in G.edges():
              c=c+1
              self.box.update()
              if self.avvio==0:
                  return
              G.remove_edge(u,v)                                                    #rimuove
              tmp_score2=scoreIniziale - ArrayScore[v] + Formula(G,v,dataset,ArrayRi[v],ArrayIndex)
              if tmp_score2<tmp_score:
                  tmp_score=tmp_score2
                  padre=u
                  figlio=v
                  tipo='remove'
            
              G.add_edge(v,u)   
              self.box.update()        
              if is_directed_acyclic_graph(G)==True and self.avvio==1:    #inverte
                  tmp_score2=tmp_score2 - ArrayScore[u] + Formula(G,u,dataset,ArrayRi[u],ArrayIndex)
                  if tmp_score2<tmp_score:
                      tmp_score=tmp_score2
                      padre=u
                      figlio=v
                      tipo='reverse'
              G.add_edge(u,v)
              self.box.delete(END)
              self.box.insert(END,'Search: '+str(int(c*100/proporzione))+'%')
              self.box.see(END)
              self.box.update()
              G.remove_edge(v,u)
              
          comp=list(complement(G).edges())
          for (u,v) in complement(G).edges():                           
              if(v,u) in G.edges():
                  c=c+1
                  self.box.delete(END)
                  self.box.insert(END,'Search: '+str(int(c*100/proporzione))+'%')
                  self.box.see(END)
                  self.box.update()
                  comp.remove((u,v))
                  
          for (u,v) in comp:         #aggiunge
               G.add_edge(u,v)
               self.box.update()
               c=c+1
               if self.avvio==0:
                   return
               if is_directed_acyclic_graph(G)==True:
                   tmp_score2=scoreIniziale - ArrayScore[v] + Formula(G,v,dataset,ArrayRi[v],ArrayIndex)
                   if tmp_score2<tmp_score:
                       tmp_score=tmp_score2
                       tipo='append'
                       padre=u
                       figlio=v
               self.box.delete(END)
               self.box.insert(END,'Search: '+str(int(c*99/proporzione))+'%')
               self.box.see(END)
               self.box.update()
               G.remove_edge(u,v)
             
          if(tipo=='remove'):
              G.remove_edge(padre,figlio)
              ArrayScore[figlio]=tmp_score - scoreIniziale + ArrayScore[figlio]
            
          elif(tipo=='reverse'):
              G.add_edge(figlio,padre)
              G.remove_edge(padre,figlio)
              ArrayScore[figlio]=Formula(G,figlio,dataset,ArrayRi[figlio],ArrayIndex)
              ArrayScore[padre]=Formula(G,padre,dataset,ArrayRi[padre],ArrayIndex)
            
          elif(tipo=='append'):
              G.add_edge(padre,figlio)
              ArrayScore[figlio]=tmp_score - scoreIniziale + ArrayScore[figlio]

          c=c+1
          self.box.delete(END)
          self.box.insert(END,'Search: '+str(int(c*99/proporzione))+'%')
          self.box.see(END)
          self.box.update()
          
          if(tipo!='not found'):
              string=str(self.iter)+') '+tipo+" ("+str(padre)+")→("+str(figlio)+")"
              self.box.delete(END)
              self.box.insert(END,string)
              string= '     score= '+str(tmp_score)
              string=string+'      '+tempo(time()-inizio_iterazione)
              self.box.insert(END,string)
              self.box.insert(END,'    ')
              self.box.see(END)
              self.Graph=G.copy()
              drawPng(G)
              self.updateImmagine(self)
              self.box.update()
       
      if(self.avvio==1):
          self.box.delete(END)
          self.box.insert(END,'  ')
          self.time=self.time+time()-self.tmptime
          string= "SCORE FINALE="+str(tmp_score)+"    "+str(tempo(self.time))
          self.box.insert(END,string)
          self.box.update()
          self.iter=0
          self.avvio=0
          self.updateImmagine(self)
          
      self.pulsanteavvio.config(text='Run')
      self.pulsantestop.config(bg='white',font=("Helvetica", self.font),borderwidth=0, relief="groove")
      self.pulsanteclear.config(bg='yellow',font=("Helvetica", self.font,'bold'),borderwidth=2, relief="groove")
      self.box.see(END)
      self.pulsanteavvio.update()
      self.pulsantestop.update()
      self.box.see(END)
      
  def Apri(self):
      f = filedialog.askopenfilename(filetypes=[("testo","*.txt"),("dat","*.dat"),("all","*.*")])
      if len(str(f))<3:
          return
      self.avvio=1
      self.box.delete(0, END)
      self.imp.grid_forget()
      self.box.insert(0,'Import dataset. Waiting...')
      self.box.update()

      in_file = open(f)
      print(in_file)
      text = in_file.read().split('\n')
      text=array(text)
      for i in range(0,len(text)):
          string=str(text[i])
          if len(string)<3:
              text=delete(text,i,0)
      self.stop(self)
      
      string=str(text[0])
      if string.count(',')>1 :
          text = array([l.split(',') for l in text])
      else:
          text = array([l.split('\t') for l in text])
      in_file.close()
      
      if (text[0][0]==' IDnum' or text[0][0]=='IDnum'):
          text=delete(text,0,1)
          
      num_var=text.shape[1]
      cases=text.shape[0]-1
      self.Graph=DiGraph()
      self.dataset=3
      self.stop(self)
      
      self.dataset=text.copy()
      self.clear(self)
      self.avvio=0
      self.empty(self)
      self.pulsanteavvio.config(bg='green',font=("Helvetica", self.font,'bold'))
      self.box.delete(0, END)
      self.casi.config(to=cases)
      self.casi.set(cases)
      self.box.grid(row=3)
      for i in range(0,self.dataset.shape[1]):
          self.Graph.add_node(self.dataset[0][i])

      self.iter=0
      self.empty(self)
      self.box.config(height=25)
      self.scrollbar.grid(row = 3, rowspan = 4, column = 5, ipady = 226)
      self.pulsanteclear.config(bg='white',font=("Helvetica", self.font),borderwidth=0, relief="groove")
      self.box.update()
      
      
  def stop(self,evento):
      if self.iter==0:
          return
      if self.avvio==0:
          return
      if self.dataset==0:
          return
      self.avvio=0
      self.box.delete(END)
      self.box.insert(END,'<PAUSA>')
      self.box.insert(END,'')
      self.box.insert(END,'')
      self.pulsanteclear.config(bg='yellow',font=("Helvetica", self.font,'bold'),borderwidth=2, relief="groove")
      self.pulsanteavvio.config(text='Run',bg='green',font=("Helvetica", self.font,'bold'),borderwidth=2, relief="groove")
      self.pulsantestop.config(bg='white',font=("Helvetica", self.font),borderwidth=0, relief="groove")
      self.box.grid(row=2,column=0,columnspan=5,rowspan=3)
      self.scrollbar.grid(row=2, ipady = 216)
      self.box.config(height=24)
      self.time=self.time+time()-self.tmptime
      self.pulsanteavvio.update()
      self.pulsantestop.update()
      self.box.see(END)
      self.box.update()

  def clear(self,evento):
      self.window.destroy()
      if self.avvio==0:
          self.iter=0
          self.Graph=self.Graph_start.copy()
          drawPng(self.Graph)
          self.updateImmagine(self)
          self.box.delete(0, END)
          self.box.grid(row=3,column=0,columnspan=5,rowspan=3)
          self.scrollbar.grid(row=3, ipady = 216)
          self.box.config(height=24)
          self.pulsanteavvio.config(text='Run',bg='green',font=("Helvetica", self.font,'bold'),borderwidth=2, relief="groove")
          self.pulsanteclear.config(bg='white',font=("Helvetica", self.font),borderwidth=0, relief="groove")
          self.box.update()
          
         
    
  def updateImmagine(self,evento):
      im=Image.open("Graph_GUI.png")
      tmp = ImageTk.PhotoImage(im)
      altezza=tmp.height()
      larghezza=tmp.width()
      max_a=633
      if altezza>max_a:
          larghezza=(larghezza*max_a)/altezza
          altezza=max_a
          
      max_l=841
      if larghezza>max_l:
          altezza=(altezza*max_l)/larghezza
          larghezza=max_l

      im = im.resize((int(larghezza),int(altezza)),Image.ANTIALIAS)
      im = ImageTk.PhotoImage(im)

      self.pulsanteimmagine.config(image=im)
      self.pulsanteimmagine.image=im
      self.pulsanteimmagine.grid(row=0,column=6,sticky=W,rowspan=6)
      self.pulsanteimmagine.update()
    
  def openImmagine(self,evento):
      os.startfile('Graph_GUI.png')

  def showDataset(self,evento):
      if self.window.winfo_exists()==1:
          return
      mythread2=Thread(target=self.sd(self)).start()
  
  def sd(self,evento):
      s=10
      string='casi= '+str(self.casi.get())+'    variabili= '+str(len(self.Graph.nodes()))
      self.window = Toplevel(root)
      self.window.iconbitmap('ico/dataset.ico')
      self.window.title("Dataset")
      if self.dataset.shape[0]>22:
          btn= zeros((self.dataset.shape[1],10))
          b=Label(self.window, text = string,font=("Helvetica", s+5))
          b.grid(row=0,column=0,columnspan=btn.shape[0]+1,sticky=W)
          for i in range(0,btn.shape[1]):
              for j in range(0,btn.shape[0]):
                  if i==0:
                      b = Label(self.window, text = str(self.dataset[i][j]),font=("Helvetica",s , "bold"),fg='white',bg='black')
                  else:
                      b = Label(self.window, text = str(self.dataset[i][j]),font=("Helvetica", s),bg='white')
                  b.grid(row=i+1,  column= j)
                  
          b = Label(self.window, text = '[...]')
          b.grid(row=12,  column= 0)
          b = Label(self.window, text = '[...]')
          b.grid(row=13,  column= 0)
          btn2= zeros((self.dataset.shape[1],10))
          c=self.dataset.shape[0]-10

          for i in range(0,btn2.shape[1]):
              for j in range(0,btn2.shape[0]):
                  b = Label(self.window, text = str(self.dataset[c+i][j]),font=("Helvetica", s),bg='white')
                  b.grid(row=14+i,  column= j)
          return
      
      btn= zeros((self.dataset.shape[1],self.dataset.shape[0]))
      b=Label(self.window, text = string,font=("Helvetica", s+5))
      b.grid(row=0,column=0,columnspan=btn.shape[0]+1,sticky=W)
      for i in range(0,btn.shape[1]):
          for j in range(0,btn.shape[0]):
              if i==0:
                  b = Label(self.window, text = str(self.dataset[i][j]),font=("Helvetica", s, "bold"),fg='white',bg='black')
              else:
                  b = Label(self.window, text = str(self.dataset[i][j]),font=("Helvetica", s),bg='white')
              b.grid(row=i+1,  column= j)
      
      
  def HC(self,evento):
      mythread=Thread(target=self.Run(self)).start()

  def empty(self,evento):
      self.null.config(font=("Helvetica", self.font, "bold"),borderwidth=2, relief="groove")
      for (u,v) in copy.deepcopy(self.Graph.edges()):
          self.Graph.remove_edge(u,v)
      self.Graph_start=self.Graph.copy()
      drawPng(self.Graph_start)
      self.updateImmagine(self)
      self.pulsanteavvio.config(text='Run',bg='green')
      self.rand.config(font=("Helvetica", self.font),borderwidth=0, relief="groove")
          
          
  def randomize(self,evento):
      self.box.insert(0,'Randomization, waiting...')
      self.box.update()
      m=Thread(target=self.r(self)).start()
      
  def r(self,evento):
      self.avvio=1
      for (u,v) in copy.deepcopy(self.Graph.edges()):
          self.Graph.remove_edge(u,v)
      self.Graph=randomEdges(self.Graph).copy()
      self.Graph_start=self.Graph.copy()
      drawPng(self.Graph)
      self.updateImmagine(self)
      self.null.config(font=("Helvetica", self.font),borderwidth=0, relief="groove")
      self.rand.config(font=("Helvetica", self.font, "bold"),borderwidth=2, relief="groove")
      self.box.delete(0)
      self.avvio=0
      
      
root = Tk()
miaApp = MiaApp(root)
root.mainloop()

