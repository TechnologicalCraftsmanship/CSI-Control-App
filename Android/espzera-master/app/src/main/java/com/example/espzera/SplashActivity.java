package com.example.espzera;

import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;
import androidx.appcompat.app.AppCompatActivity;

public class SplashActivity extends AppCompatActivity {

    private static final int SPLASH_DISPLAY_LENGTH = 5000; // 5 segundos

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_splash);

        // Usando um Handler para atrasar o início da MainActivity
        new Handler().postDelayed(new Runnable(){
            @Override
            public void run() {
                // Cria uma Intent que iniciará a MainActivity.
                Intent mainIntent = new Intent(SplashActivity.this, MainActivity.class);
                SplashActivity.this.startActivity(mainIntent);
                SplashActivity.this.finish(); // Fecha a atividade de splash para que o usuário não possa voltar a ela
            }
        }, SPLASH_DISPLAY_LENGTH);
    }
}
