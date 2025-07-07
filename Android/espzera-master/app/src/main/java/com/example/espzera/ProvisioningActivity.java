package com.example.espzera;

import android.content.Context;
import android.net.wifi.WifiInfo;
import android.net.wifi.WifiManager;
import android.os.Bundle;
import android.text.format.Formatter;
import android.view.View;
import android.widget.AdapterView;
import android.widget.Button;
import android.widget.Spinner;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import com.google.android.material.textfield.TextInputEditText;
import com.google.android.material.textfield.TextInputLayout;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class ProvisioningActivity extends AppCompatActivity {

    private TextInputEditText provSsid, provIdentity, provPassword, provServerIp, provServerPort;
    private TextInputLayout layoutProvIdentity;
    private Spinner provAuthType;
    private Button sendButton;
    private final ExecutorService executor = Executors.newSingleThreadExecutor();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_provisioning);

        provSsid = findViewById(R.id.prov_ssid);
        provIdentity = findViewById(R.id.prov_identity);
        layoutProvIdentity = findViewById(R.id.layout_prov_identity);
        provPassword = findViewById(R.id.prov_password);
        provServerIp = findViewById(R.id.prov_server_ip);
        provServerPort = findViewById(R.id.prov_server_port);
        provAuthType = findViewById(R.id.prov_auth_type);
        sendButton = findViewById(R.id.send_provision_button);

        provServerIp.setText(getLocalIpAddress());

        provAuthType.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
            @Override
            public void onItemSelected(AdapterView<?> parent, View view, int position, long id) {
                // Posição 0 = WPA2-PSK, Posição 1 = PEAP
                layoutProvIdentity.setVisibility(position == 1 ? View.VISIBLE : View.GONE);
            }
            @Override
            public void onNothingSelected(AdapterView<?> parent) {}
        });

        sendButton.setOnClickListener(v -> sendProvisionCommand());
    }

    private String getLocalIpAddress() {
        try {
            WifiManager wm = (WifiManager) getApplicationContext().getSystemService(Context.WIFI_SERVICE);
            if (wm != null) {
                WifiInfo wifiInfo = wm.getConnectionInfo();
                if (wifiInfo != null) {
                    int ipAddress = wifiInfo.getIpAddress();
                    // O IP 0 significa que não está conectado
                    if (ipAddress != 0) {
                        return Formatter.formatIpAddress(ipAddress);
                    }
                }
            }
        } catch (Exception e) {
            Toast.makeText(this, "Não foi possível obter o IP local.", Toast.LENGTH_SHORT).show();
        }
        return "192.168.1.100"; // Retorna um valor padrão se falhar
    }


    private void sendProvisionCommand() {
        String ssid = provSsid.getText().toString().trim();
        String password = provPassword.getText().toString().trim();
        String serverIp = provServerIp.getText().toString().trim();
        String serverPort = provServerPort.getText().toString().trim();
        int authTypePos = provAuthType.getSelectedItemPosition();

        if (ssid.isEmpty() || password.isEmpty() || serverIp.isEmpty() || serverPort.isEmpty()){
            Toast.makeText(this, "Por favor, preencha todos os campos.", Toast.LENGTH_SHORT).show();
            return;
        }

        String command;
        if (authTypePos == 0) { // WPA2-PSK
            command = "wpa2psk," + ssid + "," + password + "," + serverIp + "," + serverPort;
        } else { // PEAP
            String identity = provIdentity.getText().toString().trim();
            if(identity.isEmpty()){
                Toast.makeText(this, "O campo Identidade é obrigatório para WPA2-Enterprise.", Toast.LENGTH_SHORT).show();
                return;
            }
            command = "peap," + ssid + "," + identity + "," + password + "," + serverIp + "," + serverPort;
        }

        executor.execute(() -> {
            try (DatagramSocket s = new DatagramSocket()) {
                byte[] buffer = command.getBytes("UTF-8");
                // IP fixo do ESP32 em modo de provisionamento (AP Mode)
                InetAddress espAddress = InetAddress.getByName("192.168.4.1");
                DatagramPacket packet = new DatagramPacket(buffer, buffer.length, espAddress, 50000);
                s.send(packet);
                runOnUiThread(() -> {
                    Toast.makeText(ProvisioningActivity.this, "Configuração enviada! O ESP32 deve reiniciar e se conectar à rede.", Toast.LENGTH_LONG).show();
                    finish();
                });
            } catch (Exception e) {
                runOnUiThread(() -> Toast.makeText(ProvisioningActivity.this, "Falha ao enviar comando: " + e.getMessage(), Toast.LENGTH_LONG).show());
            }
        });
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        executor.shutdown();
    }
}