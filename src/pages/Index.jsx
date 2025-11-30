import { Hero } from "@/components/Hero";
import { Navigation } from "@/components/Navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { QrCode, Users, Pill, TrendingUp, Lock, AlertTriangle, CheckCircle } from "lucide-react";
import { Link } from "react-router-dom";

const Index = () => {
  const features = [
    {
      icon: QrCode,
      title: "QR Code Scanning",
      description: "Scan medicine QR codes to instantly verify authenticity, expiry dates, and manufacturer details.",
      status: "Coming Soon"
    },
    {
      icon: Pill,
      title: "Medicine Database",
      description: "Access a comprehensive database of verified medicines with detailed information and tracking.",
      status: "Coming Soon"
    },
    {
      icon: Users,
      title: "Seller Management",
      description: "Pharmaceutical companies can register and manage their medicine inventory with secure authentication.",
      status: "Coming Soon"
    },
    {
      icon: TrendingUp,
      title: "Analytics Dashboard",
      description: "Track medicine distribution, verify authenticity rates, and monitor counterfeit incidents.",
      status: "Coming Soon"
    },
    {
      icon: Lock,
      title: "Blockchain Security",
      description: "All medicines are verified and recorded on blockchain for tamper-proof authenticity.",
      status: "Coming Soon"
    },
    {
      icon: AlertTriangle,
      title: "Counterfeit Detection",
      description: "AI-powered system detects counterfeit medicines with image analysis and pattern recognition.",
      status: "Coming Soon"
    }
  ];

  const benefits = [
    {
      icon: CheckCircle,
      title: "Patient Safety",
      description: "Protect patients from fake and expired medicines"
    },
    {
      icon: Lock,
      title: "Secure Verification",
      description: "Cryptographically signed QR codes ensure authenticity"
    },
    {
      icon: TrendingUp,
      title: "Real-time Tracking",
      description: "Monitor medicine supply chain and distribution"
    }
  ];

  return (
    <main className="min-h-screen bg-background">
      <Navigation />
      <Hero />
      
      {/* Features Showcase Section */}
      <section className="py-20 px-4 bg-gradient-to-b from-background to-secondary/5">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <Badge className="mb-4">Platform Features</Badge>
            <h2 className="text-4xl font-bold mb-4">Comprehensive Medicine Verification Platform</h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Explore the features designed to ensure medicine authenticity and safety across the pharmaceutical supply chain
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, idx) => {
              const Icon = feature.icon;
              return (
                <Card key={idx} className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <div className="flex items-start justify-between mb-2">
                      <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
                        <Icon className="h-6 w-6 text-primary" />
                      </div>
                      <Badge variant="secondary">{feature.status}</Badge>
                    </div>
                    <CardTitle>{feature.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-muted-foreground">{feature.description}</p>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-20 px-4 bg-card/50">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">Why MedVerify?</h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Advanced technology designed to protect patients and pharmaceutical businesses
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {benefits.map((benefit, idx) => {
              const Icon = benefit.icon;
              return (
                <div key={idx} className="text-center">
                  <div className="w-16 h-16 bg-success/10 rounded-full flex items-center justify-center mx-auto mb-6">
                    <Icon className="h-8 w-8 text-success" />
                  </div>
                  <h3 className="text-2xl font-bold mb-2">{benefit.title}</h3>
                  <p className="text-muted-foreground">{benefit.description}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 bg-gradient-to-r from-primary/10 to-accent/10">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl font-bold mb-4">Get Started with MedVerify</h2>
          <p className="text-xl text-muted-foreground mb-8">
            Join the revolution in pharmaceutical authentication and medicine safety
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
            <Card>
              <CardHeader>
                <CardTitle className="text-base">For Patients</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-sm text-muted-foreground">Verify your medicines before use</p>
                <Link to="/login">
                  <Button className="w-full">Login to Verify</Button>
                </Link>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-base">For Sellers</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-sm text-muted-foreground">Register your medicines and manage inventory</p>
                <Link to="/register">
                  <Button className="w-full">Register as Seller</Button>
                </Link>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-base">For Admins</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-sm text-muted-foreground">Manage and verify pharmaceutical companies</p>
                <Link to="/login">
                  <Button className="w-full">Admin Login</Button>
                </Link>
              </CardContent>
            </Card>
          </div>

          <p className="text-sm text-muted-foreground">
            Already have an account? <Link to="/login" className="text-primary font-semibold hover:underline">Login here</Link>
          </p>
        </div>
      </section>
    </main>
  );
};

export default Index;
