import customtkinter as ctk
import tkinter.filedialog as filedialog
import threading
import pandas as pd
import re
import os

# --- CORES DA IDENTIDADE VISUAL ---
COR_FUNDO_CABECALHO = "#002b5e" 
COR_BOTAO_PRIMARIO = "#006db6"  
COR_BOTAO_HOVER = "#004a7c"     
COR_FUNDO_TELA = "#f4f5f7"      
COR_TEXTO_ESCURO = "#333333"

ctk.set_appearance_mode("Light")  

class ConversorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configurações da Janela Principal
        self.title("ApisulLog - Otimização e Conversão de Dados")
        self.geometry("650x450")
        self.configure(fg_color=COR_FUNDO_TELA)
        self.resizable(False, False)

        # --- CABEÇALHO ---
        self.header_frame = ctk.CTkFrame(self, fg_color=COR_FUNDO_CABECALHO, corner_radius=0, height=90)
        self.header_frame.pack(fill="x", side="top")
        
        self.title_label = ctk.CTkLabel(self.header_frame, text="SISTEMA DE CONVERSÃO DE DADOS", 
                                        text_color="white", font=("Segoe UI", 22, "bold"))
        self.title_label.pack(pady=30)

        # --- ÁREA CENTRAL (CONTEÚDO) ---
        self.main_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        self.main_frame.pack(fill="both", expand=True, padx=40, pady=30)

        self.instruction_label = ctk.CTkLabel(self.main_frame, text="Selecione a planilha (.xlsx) para iniciar a conversão:", 
                                              text_color=COR_TEXTO_ESCURO, font=("Segoe UI", 14))
        self.instruction_label.pack(pady=(30, 10), anchor="w", padx=30)

        self.file_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.file_frame.pack(fill="x", padx=30, pady=5)

        self.file_path_var = ctk.StringVar()
        self.file_entry = ctk.CTkEntry(self.file_frame, textvariable=self.file_path_var, width=350, 
                                       fg_color=COR_FUNDO_TELA, border_color="#cccccc", text_color=COR_TEXTO_ESCURO)
        self.file_entry.pack(side="left", padx=(0, 10))

        self.btn_select = ctk.CTkButton(self.file_frame, text="Procurar", command=self.selecionar_arquivo,
                                        fg_color=COR_FUNDO_CABECALHO, hover_color="#001833", width=100, font=("Segoe UI", 12, "bold"))
        self.btn_select.pack(side="left")

        self.btn_run = ctk