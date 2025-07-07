package com.example.espzera;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;

public class CadastrosActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_cadastros);

        // Inicializa os botões do sub-menu de Cadastros
        Button buttonUsuarios = findViewById(R.id.button_usuarios);
        Button buttonAmbientes = findViewById(R.id.button_ambientes);
        Button buttonLeiturasCadastros = findViewById(R.id.button_leituras_cadastros);

        // Define OnClickListener para o botão Usuários
        buttonUsuarios.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // Inicia a UsuarioManagerActivity
                Intent intent = new Intent(CadastrosActivity.this, UsuarioManagerActivity.class);
                startActivity(intent);
            }
        });

        // Define OnClickListener para o botão Ambientes
        buttonAmbientes.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Toast.makeText(CadastrosActivity.this, "Ambientes clicado!", Toast.LENGTH_SHORT).show();
                // Você iniciaria uma nova atividade aqui para gerenciar Ambientes
            }
        });

        // Define OnClickListener para o botão Leituras (dentro de Cadastros)
        buttonLeiturasCadastros.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Toast.makeText(CadastrosActivity.this, "Leituras (Cadastros) clicado!", Toast.LENGTH_SHORT).show();
                // Você iniciaria uma nova atividade aqui para gerenciar Leituras
            }
        });
    }
}
