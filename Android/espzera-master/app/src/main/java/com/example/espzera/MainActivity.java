package com.example.espzera;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import androidx.appcompat.app.AppCompatActivity;

public class MainActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // Get references to the buttons from the XML layout
        Button buttonCollect = findViewById(R.id.button_collect_data);
        Button buttonProvision = findViewById(R.id.button_provision);
        Button buttonViewData = findViewById(R.id.button_view_data);

        // Set a click listener for the "Collect Data" button
        buttonCollect.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent intent = new Intent(MainActivity.this, CollectionActivity.class);
                startActivity(intent);
            }
        });

        // Set a click listener for the "Provision ESP32" button
        buttonProvision.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent intent = new Intent(MainActivity.this, ProvisioningActivity.class);
                startActivity(intent);
            }
        });

        // Set a click listener for the "View Data" button
        buttonViewData.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent intent = new Intent(MainActivity.this, ViewDataActivity.class);
                startActivity(intent);
            }
        });
    }
}