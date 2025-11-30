import { Button } from "@/components/ui/button";
import { Shield, QrCode, Search, AlertTriangle, Sparkles } from "lucide-react";

export const Hero = () => {
  const scrollToSection = (id) => {
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  return (
    <section className="relative min-h-screen flex items-center justify-center bg-gradient-to-br from-background via-secondary/30 to-accent/20 overflow-hidden">
      {/* Decorative elements */}
      <div className="absolute inset-0 opacity-30">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-accent/5"></div>
      </div>
      
      <div className="container mx-auto px-6 relative z-10">
        <div className="text-center max-w-4xl mx-auto">
          {/* Main badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/20 mb-8">
            <Shield className="h-4 w-4 text-primary" />
            <span className="text-sm font-medium text-primary">Pharmaceutical Authentication System</span>
          </div>

          {/* Main heading */}
          <h1 className="text-5xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-foreground via-primary to-accent bg-clip-text text-transparent leading-tight">
            Verify Your 
            <span className="block">Medicine Safety</span>
          </h1>

          {/* Subheading */}
          <p className="text-xl md:text-2xl text-muted-foreground mb-12 max-w-3xl mx-auto leading-relaxed">
            Combat fake medicines, expired drugs, and mislabeling with our AI-powered 
            QR code verification system. Ensure every medicine is genuine, safe, and within expiry date.
          </p>

          {/* Action buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
            <Button
              size="lg"
              className="bg-gradient-to-r from-primary to-accent hover:shadow-medical transition-all duration-300 text-lg px-8 py-6"
              onClick={() => scrollToSection("scanner")}
            >
              <QrCode className="mr-2 h-5 w-5" />
              Scan Medicine QR Code
            </Button>
            <Button
              variant="outline"
              size="lg"
              className="border-primary text-primary hover:bg-primary/5 text-lg px-8 py-6"
              onClick={() => scrollToSection("database")}
            >
              <Search className="mr-2 h-5 w-5" />
              Search Medicine Database
            </Button>
            <Button
              variant="outline"
              size="lg"
              className="border-purple-500 text-purple-600 hover:bg-purple-50 text-lg px-8 py-6"
              onClick={() => scrollToSection("ai-assistant")}
            >
              <Sparkles className="mr-2 h-5 w-5" />
              AI Medicine Assistant
            </Button>
          </div>

          {/* Feature highlights */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            <div className="bg-card/50 backdrop-blur-sm border border-border/50 rounded-xl p-6 hover:shadow-card transition-all duration-300">
              <div className="w-12 h-12 bg-success/10 rounded-lg flex items-center justify-center mb-4 mx-auto">
                <Shield className="h-6 w-6 text-success" />
              </div>
              <h3 className="font-semibold mb-2">Authenticity Verification</h3>
              <p className="text-sm text-muted-foreground">AI-powered verification to detect counterfeit medicines instantly</p>
            </div>

            <div className="bg-card/50 backdrop-blur-sm border border-border/50 rounded-xl p-6 hover:shadow-card transition-all duration-300">
              <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4 mx-auto">
                <QrCode className="h-6 w-6 text-primary" />
              </div>
              <h3 className="font-semibold mb-2">QR Code Scanning</h3>
              <p className="text-sm text-muted-foreground">Quick and accurate medicine identification through QR codes</p>
            </div>

            <div className="bg-card/50 backdrop-blur-sm border border-border/50 rounded-xl p-6 hover:shadow-card transition-all duration-300">
              <div className="w-12 h-12 bg-warning/10 rounded-lg flex items-center justify-center mb-4 mx-auto">
                <AlertTriangle className="h-6 w-6 text-warning" />
              </div>
              <h3 className="font-semibold mb-2">Expiry Monitoring</h3>
              <p className="text-sm text-muted-foreground">Real-time alerts for expired medications and safety warnings</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};