import 'package:news_app_clean_architecture/core/resources/failure.dart';

abstract class DataState<T> {
  final T ? data;
  final Failure ? error;

  const DataState({this.data, this.error});
}

class DataSuccess<T> extends DataState<T> {
  const DataSuccess(T data) : super(data: data);
}

class DataFailed<T> extends DataState<T> {
  const DataFailed(Failure error) : super(error: error);
}
