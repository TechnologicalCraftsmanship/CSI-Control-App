package com.example.espzera;

import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.Toast;
import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import java.util.ArrayList;
import java.util.List;

public class UsuarioManagerActivity extends AppCompatActivity
        implements UsuarioAdapter.OnUserActionListener, AddEditUserDialogFragment.OnUserSavedListener {

    private DatabaseHelper dbHelper;
    private RecyclerView recyclerView;
    private UsuarioAdapter adapter;
    private List<Usuario> userList;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_usuario_manager);

        if (getSupportActionBar() != null) {
            getSupportActionBar().setTitle(R.string.usuario_manager_title);
            getSupportActionBar().setDisplayHomeAsUpEnabled(true);
        }

        dbHelper = new DatabaseHelper(this);
        recyclerView = findViewById(R.id.recycler_view_users);
        Button buttonNewUser = findViewById(R.id.button_new_user);

        userList = new ArrayList<>();
        adapter = new UsuarioAdapter(userList, this, this);
        recyclerView.setLayoutManager(new LinearLayoutManager(this));
        recyclerView.setAdapter(adapter);

        loadUsers();

        buttonNewUser.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                showAddEditUserDialog(null);
            }
        });
    }

    private void loadUsers() {
        userList = dbHelper.getAllUsuarios();
        adapter.updateUsers(userList);
        Log.d("UsuarioManagerActivity", "Usuários carregados: " + userList.size());
        if (userList.isEmpty()) {
            Toast.makeText(this, "Nenhum usuário cadastrado.", Toast.LENGTH_SHORT).show();
        }
    }

    private void showAddEditUserDialog(Usuario usuario) {
        AddEditUserDialogFragment dialogFragment;
        if (usuario == null) {
            dialogFragment = AddEditUserDialogFragment.newInstance();
        } else {
            dialogFragment = AddEditUserDialogFragment.newInstance(usuario);
        }
        dialogFragment.show(getSupportFragmentManager(), AddEditUserDialogFragment.TAG);
    }

    @Override
    public void onEditClick(Usuario usuario) {
        showAddEditUserDialog(usuario);
    }

    @Override
    public void onDeleteClick(Usuario usuario) {
        new AlertDialog.Builder(this)
                .setTitle(R.string.confirm_delete_title)
                .setMessage(getString(R.string.confirm_delete_message, usuario.getNome()))
                .setPositiveButton(R.string.yes_button, (dialog, which) -> {
                    int rowsAffected = dbHelper.deleteUsuario(usuario.getId());
                    if (rowsAffected > 0) {
                        Toast.makeText(UsuarioManagerActivity.this, "Usuário excluído: " + usuario.getNome(), Toast.LENGTH_SHORT).show();
                        loadUsers();
                    } else {
                        Toast.makeText(UsuarioManagerActivity.this, "Erro ao excluir usuário.", Toast.LENGTH_SHORT).show();
                    }
                })
                .setNegativeButton(R.string.no_button, null)
                .show();
    }

    @Override
    public void onUserSaved() {
        loadUsers();
    }
}