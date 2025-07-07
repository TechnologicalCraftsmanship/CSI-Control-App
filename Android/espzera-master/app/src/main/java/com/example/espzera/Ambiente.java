package com.example.espzera;

import java.io.Serializable;
import java.util.List; // Para pontosX e pontosY

public class Ambiente implements Serializable {
    private int id;
    private String descricao;
    private double largura;
    private double comprimento;
    private List<Double> pontosX; // Pode ser null ou vazio se não usado para a grade
    private List<Double> pontosY; // Pode ser null ou vazio se não usado para a grade
    private int status;

    // Construtor completo
    public Ambiente(int id, String descricao, double largura, double comprimento, List<Double> pontosX, List<Double> pontosY, int status) {
        this.id = id;
        this.descricao = descricao;
        this.largura = largura;
        this.comprimento = comprimento;
        this.pontosX = pontosX;
        this.pontosY = pontosY;
        this.status = status;
    }

    // Construtor para adicionar novo (sem ID, ID será auto-incrementado)
    public Ambiente(String descricao, double largura, double comprimento, List<Double> pontosX, List<Double> pontosY, int status) {
        this.descricao = descricao;
        this.largura = largura;
        this.comprimento = comprimento;
        this.pontosX = pontosX;
        this.pontosY = pontosY;
        this.status = status;
    }

    // Getters
    public int getId() {
        return id;
    }

    public String getDescricao() {
        return descricao;
    }

    public double getLargura() {
        return largura;
    }

    public double getComprimento() {
        return comprimento;
    }

    public List<Double> getPontosX() {
        return pontosX;
    }

    public List<Double> getPontosY() {
        return pontosY;
    }

    public int getStatus() {
        return status;
    }

    // Setters (se precisar alterar campos individualmente, exceto ID)
    public void setId(int id) {
        this.id = id;
    }

    public void setDescricao(String descricao) {
        this.descricao = descricao;
    }

    public void setLargura(double largura) {
        this.largura = largura;
    }

    public void setComprimento(double comprimento) {
        this.comprimento = comprimento;
    }

    public void setPontosX(List<Double> pontosX) {
        this.pontosX = pontosX;
    }

    public void setPontosY(List<Double> pontosY) {
        this.pontosY = pontosY;
    }

    public void setStatus(int status) {
        this.status = status;
    }

    @Override
    public String toString() {
        return "ID: " + id + ", Descrição: " + descricao + ", Largura: " + largura +
                ", Comprimento: " + comprimento + ", Status: " + status;
    }
}
