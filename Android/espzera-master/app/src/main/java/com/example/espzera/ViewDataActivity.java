package com.example.espzera;

import android.app.Activity;
import android.content.Intent;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.net.Uri;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;
import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.ArrayList;
import java.util.List;

public class ViewDataActivity extends AppCompatActivity {

    private static final String TAG = "ViewDataActivity";
    private Button openDbButton;
    private TextView viewingFileText, emptyView;
    private RecyclerView recyclerView;
    private CsiDataAdapter adapter;
    private final List<CsiData> csiDataList = new ArrayList<>();
    private ActivityResultLauncher<Intent> openFileLauncher;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_view_data);

        openDbButton = findViewById(R.id.button_open_db);
        viewingFileText = findViewById(R.id.text_viewing_file);
        emptyView = findViewById(R.id.text_empty_view);
        recyclerView = findViewById(R.id.recycler_view_csi_data);

        recyclerView.setLayoutManager(new LinearLayoutManager(this));
        adapter = new CsiDataAdapter(csiDataList);
        recyclerView.setAdapter(adapter);

        // Configura o lançador para abrir o seletor de arquivos
        openFileLauncher = registerForActivityResult(
                new ActivityResultContracts.StartActivityForResult(),
                result -> {
                    if (result.getResultCode() == Activity.RESULT_OK && result.getData() != null) {
                        Uri sourceUri = result.getData().getData();
                        if (sourceUri != null) {
                            viewingFileText.setText("Carregando: " + sourceUri.getPath());
                            loadDataFromUri(sourceUri);
                        }
                    }
                }
        );

        openDbButton.setOnClickListener(v -> openFilePicker());
    }

    private void openFilePicker() {
        Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT);
        intent.addCategory(Intent.CATEGORY_OPENABLE);
        intent.setType("application/vnd.sqlite3"); // Filtra por arquivos .db
        openFileLauncher.launch(intent);
    }

    private void loadDataFromUri(Uri sourceUri) {
        File tempDbFile = new File(getCacheDir(), "view_temp_csi.db");
        if (tempDbFile.exists()) {
            tempDbFile.delete();
        }

        // 1. Copia o arquivo selecionado pelo usuário para o cache do app
        try (InputStream in = getContentResolver().openInputStream(sourceUri);
             OutputStream out = new FileOutputStream(tempDbFile)) {
            byte[] buf = new byte[4096];
            int len;
            while ((len = in.read(buf)) > 0) {
                out.write(buf, 0, len);
            }
        } catch (Exception e) {
            Log.e(TAG, "Erro ao copiar DB do URI para o cache", e);
            Toast.makeText(this, "Não foi possível abrir o arquivo.", Toast.LENGTH_SHORT).show();
            return;
        }

        csiDataList.clear();

        // 2. Abre o banco de dados temporário e lê os dados
        try (SQLiteDatabase db = SQLiteDatabase.openDatabase(tempDbFile.getPath(), null, SQLiteDatabase.OPEN_READONLY);
             Cursor cursor = db.rawQuery("SELECT * FROM csi_data ORDER BY id DESC", null)) {

            if (cursor.moveToFirst()) {
                do {
                    // *** CORREÇÃO AQUI: Preenchendo todos os 28 campos do construtor ***
                    CsiData data = new CsiData(
                            cursor.getInt(cursor.getColumnIndexOrThrow("id")),
                            cursor.getString(cursor.getColumnIndexOrThrow("data_hora")),
                            cursor.getString(cursor.getColumnIndexOrThrow("cenario")),
                            cursor.getString(cursor.getColumnIndexOrThrow("type")),
                            cursor.getString(cursor.getColumnIndexOrThrow("mac")),
                            cursor.getInt(cursor.getColumnIndexOrThrow("seq")),
                            cursor.getInt(cursor.getColumnIndexOrThrow("rssi")),
                            cursor.getFloat(cursor.getColumnIndexOrThrow("rate")),
                            cursor.getInt(cursor.getColumnIndexOrThrow("sig_mode")),
                            cursor.getInt(cursor.getColumnIndexOrThrow("mcs")),
                            cursor.getInt(cursor.getColumnIndexOrThrow("bandwidth")),
                            cursor.getInt(cursor.getColumnIndexOrThrow("smoothing")),
                            cursor.getInt(cursor.getColumnIndexOrThrow("not_sounding")),
                            cursor.getInt(cursor.getColumnIndexOrThrow("aggregation")),
                            cursor.getInt(cursor.getColumnIndexOrThrow("stbc")),
                            cursor.getInt(cursor.getColumnIndexOrThrow("fec_coding")),
                            cursor.getInt(cursor.getColumnIndexOrThrow("sgi")),
                            cursor.getInt(cursor.getColumnIndexOrThrow("noise_floor")),
                            cursor.getInt(cursor.getColumnIndexOrThrow("ampdu_cnt")),
                            cursor.getInt(cursor.getColumnIndexOrThrow("channel")),
                            cursor.getInt(cursor.getColumnIndexOrThrow("secondary_channel")),
                            cursor.getLong(cursor.getColumnIndexOrThrow("local_timestamp")),
                            cursor.getInt(cursor.getColumnIndexOrThrow("ant")),
                            cursor.getInt(cursor.getColumnIndexOrThrow("sig_len")),
                            cursor.getInt(cursor.getColumnIndexOrThrow("rx_state")),
                            cursor.getInt(cursor.getColumnIndexOrThrow("len")),
                            cursor.getInt(cursor.getColumnIndexOrThrow("first_word")),
                            cursor.getString(cursor.getColumnIndexOrThrow("data"))
                    );
                    csiDataList.add(data);
                } while (cursor.moveToNext());
            }
        } catch (Exception e) {
            Log.e(TAG, "Erro ao ler do banco de dados temporário", e);
            Toast.makeText(this, "Erro ao ler o arquivo de banco de dados. Verifique se o formato está correto.", Toast.LENGTH_LONG).show();
        } finally {
            tempDbFile.delete(); // Apaga a cópia temporária
        }

        adapter.updateData(csiDataList);
        emptyView.setVisibility(csiDataList.isEmpty() ? View.VISIBLE : View.GONE);
        recyclerView.setVisibility(csiDataList.isEmpty() ? View.GONE : View.VISIBLE);
        viewingFileText.setText("Visualizando " + csiDataList.size() + " registros.");
    }
}