export default function TermsPage() {
  return (
    <div className="py-16 md:py-24">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold mb-8">Terms of Service</h1>
        <div className="prose dark:prose-invert max-w-none">
          <p className="text-lg text-foreground/70 mb-8">
            These terms govern your use of FineData services. By using our platform, you agree to these terms.
          </p>

          <h2>Service Description</h2>
          <p>
            FineData provides AI-powered dataset creation services using web crawling and processing technologies to generate custom training datasets.
          </p>

          <h2>User Responsibilities</h2>
          <p>
            Users are responsible for ensuring their use of generated datasets complies with applicable laws and regulations. Datasets should not be used for illegal activities.
          </p>

          <h2>Intellectual Property</h2>
          <p>
            Users retain ownership of their generated datasets. FineData retains ownership of the platform and processing algorithms.
          </p>

          <h2>Limitation of Liability</h2>
          <p>
            FineData provides services on an "as-is" basis. We strive for high quality but cannot guarantee perfect dataset accuracy or completeness.
          </p>

          <p className="text-sm text-foreground/60 mt-8">
            These terms are subject to updates. Continued use of our services constitutes acceptance of updated terms.
          </p>
        </div>
      </div>
    </div>
  );
}
