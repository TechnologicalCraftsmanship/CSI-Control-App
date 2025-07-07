package com.example.espzera;

import android.app.Dialog;
import android.content.Context;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.appcompat.app.AlertDialog;
import androidx.fragment.app.DialogFragment;

public class AddEditUserDialogFragment extends DialogFragment {

    public static final String TAG = "AddEditUserDialogFragment";
    private static final String ARG_USER = "user_object";

    private EditText etName, etNickname;
    private Spinner spinnerStatus;
    private TextView dialogTitle;
    private Usuario currentUser;
    private OnUserSavedListener listener;

    public interface OnUserSavedListener {
        void onUserSaved();
    }

    public static AddEditUserDialogFragment newInstance() {
        return new AddEditUserDialogFragment();
    }

    public static AddEditUserDialogFragment newInstance(Usuario user) {
        AddEditUserDialogFragment fragment = new AddEditUserDialogFragment();
        Bundle args = new Bundle();
        args.putSerializable(ARG_USER, user);
        fragment.setArguments(args);
        return fragment;
    }

    @Override
    public void onAttach(@NonNull Context context) {
        super.onAttach(context);
        if (context instanceof OnUserSavedListener) {
            listener = (OnUserSavedListener) context;
        } else {
            throw new RuntimeException(context.toString() + " must implement OnUserSavedListener");
        }
    }

    @Override
    public void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        if (getArguments() != null) {
            currentUser = (Usuario) getArguments().getSerializable(ARG_USER);
        }
    }

    @NonNull
    @Override
    public Dialog onCreateDialog(@Nullable Bundle savedInstanceState) {
        AlertDialog.Builder builder = new AlertDialog.Builder(requireActivity());
        LayoutInflater inflater = requireActivity().getLayoutInflater();
        View view = inflater.inflate(R.layout.dialog_add_edit_user, null);

        dialogTitle = view.findViewById(R.id.dialog_title);
        etName = view.findViewById(R.id.edit_text_dialog_user_name);
        etNickname = view.findViewById(R.id.edit_text_dialog_user_nickname);
        spinnerStatus = view.findViewById(R.id.spinner_dialog_user_status);
        Button btnSave = view.findViewById(R.id.button_dialog_save);
        Button btnCancel = view.findViewById(R.id.button_dialog_cancel);

        ArrayAdapter<CharSequence> adapter = ArrayAdapter.createFromResource(
                requireContext(),
                R.array.status_options,
                android.R.layout.simple_spinner_item
        );
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        spinnerStatus.setAdapter(adapter);


        if (currentUser != null) {
            dialogTitle.setText(R.string.dialog_edit_user_title);
            etName.setText(currentUser.getNome());
            etNickname.setText(currentUser.getApelido());
            if (currentUser.getStatus() == 0) {
                spinnerStatus.setSelection(0); // "0 - Inativo"
            } else {
                spinnerStatus.setSelection(1); // "1 - Ativo"
            }
        } else {
            dialogTitle.setText(R.string.dialog_add_user_title);
            spinnerStatus.setSelection(1); // Define "Ativo" como padrão para novos usuários
        }

        btnSave.setOnClickListener(v -> saveUser());
        btnCancel.setOnClickListener(v -> dismiss()); // Fecha o diálogo

        builder.setView(view);
        return builder.create();
    }

    private void saveUser() {
        String name = etName.getText().toString().trim();
        String nickname = etNickname.getText().toString().trim();
        int status = spinnerStatus.getSelectedItemPosition();

        if (name.isEmpty() || nickname.isEmpty()) {
            Toast.makeText(getContext(), "Por favor, preencha o nome e o apelido.", Toast.LENGTH_SHORT).show();
            return;
        }

        DatabaseHelper dbHelper = new DatabaseHelper(getContext());
        long result = -1;

        if (currentUser != null) {
            currentUser.setNome(name);
            currentUser.setApelido(nickname);
            currentUser.setStatus(status);
            result = dbHelper.updateUsuario(currentUser);
            if (result > 0) {
                Toast.makeText(getContext(), "Usuário atualizado com sucesso!", Toast.LENGTH_SHORT).show();
            } else {
                Toast.makeText(getContext(), "Erro ao atualizar usuário.", Toast.LENGTH_SHORT).show();
            }
        } else {
            result = dbHelper.addUsuario(name, nickname, status);
            if (result != -1) {
                Toast.makeText(getContext(), "Usuário adicionado com ID: " + result, Toast.LENGTH_SHORT).show();
            } else {
                Toast.makeText(getContext(), "Erro ao adicionar usuário.", Toast.LENGTH_SHORT).show();
            }
        }

        if (result != -1) {
            listener.onUserSaved();
            dismiss();
        }
    }
}