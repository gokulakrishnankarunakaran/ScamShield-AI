import 'package:flutter_test/flutter_test.dart';
import 'package:app/app.dart';

void main() {
  testWidgets('ScamShieldApp smoke test', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const ScamShieldApp());

    // Verify app title and principle are rendered
    expect(find.text('SCAMSHIELD AI'), findsOneWidget);
    expect(find.text('VERIFY BEFORE YOU TRUST'), findsOneWidget);
    expect(find.text('TEAM CYBERTRON'), findsOneWidget);
  });
}
