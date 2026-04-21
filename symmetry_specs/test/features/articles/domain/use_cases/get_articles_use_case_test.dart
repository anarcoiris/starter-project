import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';

// TODO: import your use case and mock repository here

class MockArticlesRepository extends Mock {
  // implements ArticlesRepository
}

void main() {
  late MockArticlesRepository mockRepo;

  setUp(() {
    mockRepo = MockArticlesRepository();
  });

  group('GetArticlesUseCase', () {
    test('returns list of articles on success', () async {
      // arrange
      // when(mockRepo.getAll()).thenAnswer((_) async => [...]);
      // act
      // assert
    });
  });
}
