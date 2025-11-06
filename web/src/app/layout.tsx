import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { QueryProvider } from "@/components/providers/query-provider";
import { ThemeProvider } from "@/components/providers/theme-provider";
import { AccessibilityProvider } from "@/components/providers/accessibility-provider";
import { MainNav, SkipLink } from "@/components/nav/MainNav";
import { Footer } from "@/components/nav/Footer";
import { I18nProvider } from "@/lib/i18n";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

export const metadata: Metadata = {
  title: "FineData - Custom Domain Datasets",
  description: "Generate high-quality, domain-specific datasets from billions of web pages—ready for training specialized AI models, research, and analytics.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.variable} font-sans antialiased`}>
        <ThemeProvider
          attribute="class"
          defaultTheme="light"
          enableSystem={false}
          disableTransitionOnChange
        >
          <I18nProvider>
            <AccessibilityProvider>
              <SkipLink />
              <QueryProvider>
              <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white dark:from-slate-950 dark:to-slate-900">
                <MainNav />
                          <main id="main-content" className="mx-auto w-full max-w-6xl px-4 md:px-6 lg:px-8">
                            {children}
                          </main>
                          <Footer />
              </div>
              </QueryProvider>
            </AccessibilityProvider>
          </I18nProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
