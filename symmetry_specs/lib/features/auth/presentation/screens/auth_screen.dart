import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../bloc/auth_cubit.dart';
import '../bloc/auth_state.dart';
import '../widgets/auth_list_widget.dart';

class AuthScreen extends StatefulWidget {
  const AuthScreen({super.key});

  @override
  State<AuthScreen> createState() => _AuthScreenState();
}

class _AuthScreenState extends State<AuthScreen> {
  @override
  void initState() {
    super.initState();
    context.read<AuthCubit>().loadAuths();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Auth')),
      body: BlocBuilder<AuthCubit, AuthState>(
        builder: (context, state) {
          return switch (state) {
            AuthLoading() => const Center(child: CircularProgressIndicator()),
            AuthLoaded(items: final items) => AuthListWidget(items: items),
            AuthError(message: final msg) => Center(child: Text(msg)),
            _ => const SizedBox.shrink(),
          };
        },
      ),
    );
  }
}
