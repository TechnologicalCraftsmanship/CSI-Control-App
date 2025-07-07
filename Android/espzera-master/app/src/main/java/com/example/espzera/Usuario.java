package com.example.espzera;

import java.io.Serializable; // Para passar o objeto entre Activities/Fragments

    public class Usuario implements Serializable { // Implementa Serializable para passagem em Bundles
        private int id;
        private String nome;
        private String apelido;
        private int status; // 0 para inativo, 1 para ativo ou outro status numérico

        public Usuario(int id, String nome, String apelido, int status) {
            this.id = id;
            this.nome = nome;
            this.apelido = apelido;
            this.status = status;
        }

        // Construtor para novos usuários (sem ID, ID será auto-incrementado pelo BD)
        public Usuario(String nome, String apelido, int status) {
            this.nome = nome;
            this.apelido = apelido;
            this.status = status;
        }

        // Getters
        public int getId() {
            return id;
        }

        public String getNome() {
            return nome;
        }

        public String getApelido() {
            return apelido;
        }

        public int getStatus() {
            return status;
        }

        // Setters (se precisar alterar campos individualmente, exceto ID)
        public void setNome(String nome) {
            this.nome = nome;
        }

        public void setApelido(String apelido) {
            this.apelido = apelido;
        }

        public void setStatus(int status) {
            this.status = status;
        }

        // Setter para ID (usado principalmente ao ler do BD para um objeto novo)
        public void setId(int id) {
            this.id = id;
        }

        @Override
        public String toString() {
            return "ID: " + id + ", Nome: " + nome + ", Apelido: " + apelido + ", Status: " + status;
        }
    }