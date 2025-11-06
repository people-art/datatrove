export default function PrivacyPage() {
  return (
    <div className="py-16 md:py-24">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold mb-8">Privacy Policy</h1>
        <div className="prose dark:prose-invert max-w-none">
          <p className="text-lg text-foreground/70 mb-8">
            Your privacy is important to us. This policy explains how FineData collects, uses, and protects your data.
          </p>

          <h2>Data Collection</h2>
          <p>
            We collect minimal personal information necessary to provide our services, including email addresses for delivery notifications and basic usage analytics.
          </p>

          <h2>Data Usage</h2>
          <p>
            Your data is used solely for providing our dataset creation services and improving our platform. We never sell personal data to third parties.
          </p>

          <h2>Data Security</h2>
          <p>
            All data is encrypted in transit and at rest. We follow industry best practices for data security and compliance.
          </p>

          <p className="text-sm text-foreground/60 mt-8">
            This privacy policy is subject to updates. Please check back regularly for changes.
          </p>
        </div>
      </div>
    </div>
  );
}
