import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../bloc/articles_cubit.dart';
import '../bloc/articles_state.dart';
import '../widgets/articles_list_widget.dart';

class ArticlesScreen extends StatefulWidget {
  const ArticlesScreen({super.key});

  @override
  State<ArticlesScreen> createState() => _ArticlesScreenState();
}

class _ArticlesScreenState extends State<ArticlesScreen> {
  @override
  void initState() {
    super.initState();
    context.read<ArticlesCubit>().loadArticles();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Articles')),
      body: BlocBuilder<ArticlesCubit, ArticlesState>(
        builder: (context, state) {
          return switch (state) {
            ArticlesLoading() => const Center(child: CircularProgressIndicator()),
            ArticlesLoaded(items: final items) => ArticlesListWidget(items: items),
            ArticlesError(message: final msg) => Center(child: Text(msg)),
            _ => const SizedBox.shrink(),
          };
        },
      ),
    );
  }
}
