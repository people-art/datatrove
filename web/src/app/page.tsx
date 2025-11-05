import { Hero } from "@/components/sections/Hero";
import { SellingPoints } from "@/components/sections/SellingPoints";
import { ProcessSteps } from "@/components/sections/ProcessSteps";

export default function Home() {
  return (
    <div className="min-h-screen">
      <Hero />
      <SellingPoints />
      <ProcessSteps />
    </div>
  );
}
