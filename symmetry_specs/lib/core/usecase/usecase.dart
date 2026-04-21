/// Base class for all use cases.
/// [Type]   — the return type wrapped in DataState.
/// [Params] — the input parameters (use NoParams when none needed).
abstract class UseCase<Type, Params> {
  Future<DataState<Type>> call(Params params);
}

class NoParams {
  const NoParams();
}
