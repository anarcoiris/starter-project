import 'package:flutter/material.dart';
import '../../domain/entities/auth_entity.dart';

class AuthListWidget extends StatelessWidget {
  final List<AuthEntity> items;
  const AuthListWidget({super.key, required this.items});

  @override
  Widget build(BuildContext context) {
    if (items.isEmpty) {
      return const Center(child: Text('No items yet.'));
    }
    return ListView.builder(
      itemCount: items.length,
      itemBuilder: (_, i) => ListTile(title: Text(items[i].id)),
    );
  }
}
