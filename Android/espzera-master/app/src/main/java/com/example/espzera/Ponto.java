package com.example.espzera;

import java.io.Serializable;

public class Ponto implements Serializable {
    private int id;
    private int idAmbiente;
    private int numero;
    private double posicaoX;
    private double posicaoY;
    private int status;

    // Construtor completo
    public Ponto(int id, int idAmbiente, int numero, double posicaoX, double posicaoY, int status) {
        this.id = id;
        this.idAmbiente = idAmbiente;
        this.numero = numero;
        this.posicaoX = posicaoX;
        this.posicaoY = posicaoY;
        this.status = status;
    }

    // Construtor para adicionar novo (sem ID, ID será auto-incrementado)
    public Ponto(int idAmbiente, int numero, double posicaoX, double posicaoY, int status) {
        this.idAmbiente = idAmbiente;
        this.numero = numero;
        this.posicaoX = posicaoX;
        this.posicaoY = posicaoY;
        this.status = status;
    }

    // Getters
    public int getId() {
        return id;
    }

    public int getIdAmbiente() {
        return idAmbiente;
    }

    public int getNumero() {
        return numero;
    }

    public double getPosicaoX() {
        return posicaoX;
    }

    public double getPosicaoY() {
        return posicaoY;
    }

    public int getStatus() {
        return status;
    }

    // Setters
    public void setId(int id) {
        this.id = id;
    }

    public void setIdAmbiente(int idAmbiente) {
        this.idAmbiente = idAmbiente;
    }

    public void setNumero(int numero) {
        this.numero = numero;
    }

    public void setPosicaoX(double posicaoX) {
        this.posicaoX = posicaoX;
    }

    public void setPosicaoY(double posicaoY) {
        this.posicaoY = posicaoY;
    }

    public void setStatus(int status) {
        this.status = status;
    }

    @Override
    public String toString() {
        return "ID: " + id + ", Ambiente ID: " + idAmbiente + ", Número: " + numero +
                ", Posição X: " + posicaoX + ", Posição Y: " + posicaoY + ", Status: " + status;
    }
}
