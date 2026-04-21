import 'package:flutter/material.dart';
import '../../domain/entities/articles_entity.dart';

class ArticlesListWidget extends StatelessWidget {
  final List<ArticlesEntity> items;
  const ArticlesListWidget({super.key, required this.items});

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
