import 'package:equatable/equatable.dart';
import '../../domain/entities/articles_entity.dart';

sealed class ArticlesState extends Equatable {
  const ArticlesState();

  @override
  List<Object?> get props => [];
}

class ArticlesInitial extends ArticlesState {
  const ArticlesInitial();
}

class ArticlesLoading extends ArticlesState {
  const ArticlesLoading();
}

class ArticlesLoaded extends ArticlesState {
  final List<ArticlesEntity> items;
  const ArticlesLoaded(this.items);

  @override
  List<Object?> get props => [items];
}

class ArticlesError extends ArticlesState {
  final String message;
  const ArticlesError(this.message);

  @override
  List<Object?> get props => [message];
}
