package com.example.espzera;

import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;
import android.util.Log;

import java.util.ArrayList;
import java.util.List;

public class DatabaseHelper extends SQLiteOpenHelper {

    private static final String DATABASE_NAME = "esp_app_internal.db";
    private static final int DATABASE_VERSION = 1;
    private static final String TAG = "DatabaseHelper";

    // Nomes das tabelas
    public static final String TABLE_USUARIO = "usuario";
    public static final String TABLE_CSI_DATA = "csi_data";

    // Colunas da tabela USUARIO
    public static final String COL_USUARIO_ID = "id";
    public static final String COL_USUARIO_NOME = "nome";
    public static final String COL_USUARIO_APELIDO = "apelido";
    public static final String COL_USUARIO_STATUS = "status";

    public DatabaseHelper(Context context) {
        super(context, DATABASE_NAME, null, DATABASE_VERSION);
    }

    @Override
    public void onCreate(SQLiteDatabase db) {
        String CREATE_TABLE_USUARIO_SQL = "CREATE TABLE " + TABLE_USUARIO + "("
                + COL_USUARIO_ID + " INTEGER PRIMARY KEY AUTOINCREMENT,"
                + COL_USUARIO_NOME + " TEXT,"
                + COL_USUARIO_APELIDO + " TEXT,"
                + COL_USUARIO_STATUS + " INTEGER" + ")";
        db.execSQL(CREATE_TABLE_USUARIO_SQL);
        createCsiDataTable(db);
    }

    @Override
    public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
        db.execSQL("DROP TABLE IF EXISTS " + TABLE_USUARIO);
        db.execSQL("DROP TABLE IF EXISTS " + TABLE_CSI_DATA);
        onCreate(db);
    }

    // --- MÉTODOS CRUD COMPLETOS PARA USUÁRIOS (Banco Interno) ---

    public long addUsuario(String nome, String apelido, int status) {
        SQLiteDatabase db = this.getWritableDatabase();
        ContentValues values = new ContentValues();
        values.put(COL_USUARIO_NOME, nome);
        values.put(COL_USUARIO_APELIDO, apelido);
        values.put(COL_USUARIO_STATUS, status);
        long id = db.insert(TABLE_USUARIO, null, values);
        db.close();
        return id;
    }

    public List<Usuario> getAllUsuarios() {
        List<Usuario> userList = new ArrayList<>();
        SQLiteDatabase db = this.getReadableDatabase();
        try (Cursor cursor = db.rawQuery("SELECT * FROM " + TABLE_USUARIO, null)) {
            if (cursor.moveToFirst()) {
                do {
                    int id = cursor.getInt(cursor.getColumnIndexOrThrow(COL_USUARIO_ID));
                    String nome = cursor.getString(cursor.getColumnIndexOrThrow(COL_USUARIO_NOME));
                    String apelido = cursor.getString(cursor.getColumnIndexOrThrow(COL_USUARIO_APELIDO));
                    int status = cursor.getInt(cursor.getColumnIndexOrThrow(COL_USUARIO_STATUS));
                    userList.add(new Usuario(id, nome, apelido, status));
                } while (cursor.moveToNext());
            }
        }
        db.close();
        return userList;
    }

    public int updateUsuario(Usuario usuario) {
        SQLiteDatabase db = this.getWritableDatabase();
        ContentValues values = new ContentValues();
        values.put(COL_USUARIO_NOME, usuario.getNome());
        values.put(COL_USUARIO_APELIDO, usuario.getApelido());
        values.put(COL_USUARIO_STATUS, usuario.getStatus());
        int rowsAffected = db.update(TABLE_USUARIO, values, COL_USUARIO_ID + " = ?", new String[]{String.valueOf(usuario.getId())});
        db.close();
        return rowsAffected;
    }

    public int deleteUsuario(int id) {
        SQLiteDatabase db = this.getWritableDatabase();
        int rowsAffected = db.delete(TABLE_USUARIO, COL_USUARIO_ID + " = ?", new String[]{String.valueOf(id)});
        db.close();
        return rowsAffected;
    }


    // --- MÉTODOS DE AJUDA ESTÁTICOS (Para os arquivos .db externos) ---

    public static void createCsiDataTable(SQLiteDatabase db) {
        String CREATE_TABLE_CSI_DATA_SQL = "CREATE TABLE IF NOT EXISTS " + TABLE_CSI_DATA + " (id INTEGER PRIMARY KEY AUTOINCREMENT, data_hora TEXT, cenario TEXT, type TEXT, mac TEXT, seq INTEGER, rssi INTEGER, rate REAL, sig_mode INTEGER, mcs INTEGER, bandwidth INTEGER, smoothing INTEGER, not_sounding INTEGER, aggregation INTEGER, stbc INTEGER, fec_coding INTEGER, sgi INTEGER, noise_floor INTEGER, ampdu_cnt INTEGER, channel INTEGER, secondary_channel INTEGER, local_timestamp INTEGER, ant INTEGER, sig_len INTEGER, rx_state INTEGER, len INTEGER, first_word INTEGER, data TEXT)";
        db.execSQL(CREATE_TABLE_CSI_DATA_SQL);
    }

    /**
     * Adiciona uma nova linha de dados CSI a um banco de dados fornecido.
     * Este método é estático para ser usado com instâncias de banco de dados externos/temporários.
     *
     * @param db O banco de dados SQLite onde os dados serão inseridos.
     * @param dataHora O timestamp da coleta.
     * @param cenario A descrição do cenário da coleta.
     * @param csiParts Um array de Strings contendo os dados CSI, começando por 'seq'.
     * @return O ID da linha inserida, ou -1 em caso de erro.
     */
    public static long addCsiData(SQLiteDatabase db, String dataHora, String cenario, String[] csiParts) {
        // O payload que chega aqui (csiParts) deve ter 24 campos (de seq até data).
        // Ajustamos a validação para o número correto de campos no payload.
        if (csiParts == null || csiParts.length < 24) {
            Log.e(TAG, "Pacote CSI inválido descartado. Esperava >= 24 campos de payload, mas recebeu " + (csiParts != null ? csiParts.length : 0));
            return -1;
        }

        // Limpa as aspas, se houver, de cada parte dos dados.
        for (int i = 0; i < csiParts.length; i++) {
            if (csiParts[i] != null) {
                csiParts[i] = csiParts[i].trim().replace("\"", "");
            }
        }

        ContentValues values = new ContentValues();
        try {
            // --- CÓDIGO CORRIGIDO ---
            // A ordem de inserção agora corresponde à ordem do payload recebido (csiParts),
            // onde csiParts[0] = seq, csiParts[1] = mac, e assim por diante.

            values.put("data_hora", dataHora);
            values.put("cenario", cenario);
            values.put("type", "CSI_DATA"); // Adiciona o tipo de volta, que foi removido na Activity
            values.put("seq", Integer.parseInt(csiParts[0]));
            values.put("mac", csiParts[1]);
            values.put("rssi", Integer.parseInt(csiParts[2]));
            values.put("rate", Float.parseFloat(csiParts[3]));
            values.put("sig_mode", Integer.parseInt(csiParts[4]));
            values.put("mcs", Integer.parseInt(csiParts[5]));
            values.put("bandwidth", Integer.parseInt(csiParts[6]));
            values.put("smoothing", Integer.parseInt(csiParts[7]));
            values.put("not_sounding", Integer.parseInt(csiParts[8]));
            values.put("aggregation", Integer.parseInt(csiParts[9]));
            values.put("stbc", Integer.parseInt(csiParts[10]));
            values.put("fec_coding", Integer.parseInt(csiParts[11]));
            values.put("sgi", Integer.parseInt(csiParts[12]));
            values.put("noise_floor", Integer.parseInt(csiParts[13]));
            values.put("ampdu_cnt", Integer.parseInt(csiParts[14]));
            values.put("channel", Integer.parseInt(csiParts[15]));
            values.put("secondary_channel", Integer.parseInt(csiParts[16]));
            values.put("local_timestamp", Long.parseLong(csiParts[17]));
            values.put("ant", Integer.parseInt(csiParts[18]));
            values.put("sig_len", Integer.parseInt(csiParts[19]));
            values.put("rx_state", Integer.parseInt(csiParts[20]));
            values.put("len", Integer.parseInt(csiParts[21]));
            values.put("first_word", Integer.parseInt(csiParts[22]));
            
            // Verifica se o campo 'data' existe antes de tentar acessá-lo.
            if (csiParts.length > 23) {
                values.put("data", csiParts[23]); 
            } else {
                values.put("data", ""); // Insere um valor vazio se o campo não existir
            }
            
        } catch (NumberFormatException e) {
            Log.e(TAG, "Erro de formatação de número ao parsear dados CSI: " + e.getMessage() + " | Dados: " + String.join(",", csiParts));
            return -1;
        } catch (Exception e) {
            Log.e(TAG, "Erro genérico ao preparar dados CSI para inserção: " + e.getMessage());
            return -1;
        }
        
        return db.insert(TABLE_CSI_DATA, null, values);
    }
}
