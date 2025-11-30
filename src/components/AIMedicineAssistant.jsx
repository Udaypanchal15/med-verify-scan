import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { 
  Bot, 
  Send, 
  MessageCircle, 
  Sparkles, 
  Pill, 
  AlertCircle,
  CheckCircle,
  Info
} from "lucide-react";
import { medicines } from "@/data/medicines";
import { toast } from "@/hooks/use-toast";

export const AIMedicineAssistant = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: "ai",
      content: "Hello! I'm your AI Medicine Assistant. I can help you find medicines, answer questions about medications, and provide recommendations based on our comprehensive database. What would you like to know?",
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const scrollAreaRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);

  const getAIResponse = (userMessage) => {
    const query = userMessage.toLowerCase();
    
    // Q&A: "what is X used for" or "what is X"
    const usedForMatch = query.match(/what\s+is\s+([a-z0-9\s%]+)\s*(used\s*for)?\??/);
    if (usedForMatch) {
      const term = usedForMatch[1].trim();
      const med = medicines.find(m => 
        m.name.toLowerCase().includes(term) ||
        (m.activeIngredient && m.activeIngredient.toLowerCase().includes(term))
      );
      if (med) {
        const info = `"${med.name}" is typically used for ${
          med.category === 'Antihistamine' ? 'allergy relief (sneezing, runny nose, itching)'
          : med.category === 'Analgesic' ? 'pain relief and fever reduction'
          : med.category === 'NSAID' ? 'pain, inflammation, and fever'
          : med.category === 'Antibiotic' ? 'treating bacterial infections'
          : med.category === 'Proton Pump Inhibitor' ? 'acid reflux and heartburn'
          : med.category === 'Antitussive' ? 'cough suppression'
          : med.category === 'Bronchodilator' ? 'relieving bronchospasm and easing breathing'
          : med.category === 'Cardiovascular' ? 'controlling blood pressure and heart conditions'
          : med.category === 'Statin' ? 'lowering cholesterol to reduce heart risk'
          : med.category === 'Antidiabetic' ? 'lowering blood sugar in type 2 diabetes'
          : med.category === 'Insulin' ? 'blood glucose control in diabetes'
          : 'its indicated condition'
        }.`;
        return { type: 'ai', content: `${info}\n\nManufacturer: ${med.manufacturer}\nActive ingredient: ${med.activeIngredient}\nForm/Strength: ${med.dosageForm}, ${med.strength}\nTypical price: ${med.price}` };
      }
    }
    
    // Medicine search functionality
    if (query.includes("find") || query.includes("search") || query.includes("medicine for")) {
      const searchTerms = query.split(/find|search|medicine for/)[1]?.trim();
      if (searchTerms) {
        const results = medicines.filter(med => 
          med.name.toLowerCase().includes(searchTerms) ||
          med.activeIngredient.toLowerCase().includes(searchTerms) ||
          med.category.toLowerCase().includes(searchTerms) ||
          med.description.toLowerCase().includes(searchTerms)
        ).slice(0, 3);

        if (results.length > 0) {
          return {
            type: "ai",
            content: `I found ${results.length} medicine(s) related to "${searchTerms}":`,
            recommendations: results
          };
        } else {
          return {
            type: "ai",
            content: `I couldn't find any medicines matching "${searchTerms}". Try searching with different keywords like pain relief, fever, cough, etc.`
          };
        }
      }
    }

    // Price comparison
    if (query.includes("price") || query.includes("cost") || query.includes("expensive")) {
      const expensiveMeds = medicines.filter(med => 
        med.price && parseFloat(med.price.replace("₹", "")) > 100
      ).slice(0, 3);
      
      return {
        type: "ai",
        content: "Here are some higher-priced medicines in our database (above ₹100):",
        recommendations: expensiveMeds
      };
    }

    // Category-based recommendations
    if (query.includes("pain") || query.includes("headache")) {
      const painMeds = medicines.filter(med => 
        med.category === "Analgesic" || med.category === "NSAID"
      ).slice(0, 3);
      
      return {
        type: "ai",
        content: "For pain relief, I recommend these medicines:",
        recommendations: painMeds
      };
    }

    if (query.includes("allergy") || query.includes("sneeze") || query.includes("itch")) {
      const allergy = medicines.filter(med => med.category === 'Antihistamine').slice(0,3);
      return { type: 'ai', content: 'For allergy symptoms, consider these antihistamines:', recommendations: allergy };
    }

    if (query.includes("heartburn") || query.includes("acidity") || query.includes("acid reflux")) {
      const acid = medicines.filter(med => med.category === 'Proton Pump Inhibitor').slice(0,3);
      return { type: 'ai', content: 'For acidity and heartburn, these are commonly used:', recommendations: acid };
    }

    if (query.includes("blood pressure") || query.includes("hypertension") || query.includes("bp")) {
      const bp = medicines.filter(med => med.category === 'Cardiovascular').slice(0,3);
      return { type: 'ai', content: 'For high blood pressure, these medicines are used under medical supervision:', recommendations: bp };
    }

    if (query.includes("cholesterol") || query.includes("lipid")) {
      const chol = medicines.filter(med => med.category === 'Statin').slice(0,3);
      return { type: 'ai', content: 'For high cholesterol, these statins are commonly prescribed:', recommendations: chol };
    }

    if (query.includes("diabetes") || query.includes("blood sugar") || query.includes("glucose")) {
      const diab = medicines.filter(med => med.category === 'Antidiabetic' || med.category === 'Insulin').slice(0,3);
      return { type: 'ai', content: 'For diabetes management, here are common options (consult your doctor):', recommendations: diab };
    }

    if (query.includes("dehydration") || query.includes("rehydration") || query.includes("diarrhea")) {
      const ors = medicines.filter(med => med.name.toLowerCase().includes('ors') || med.activeIngredient?.toLowerCase().includes('oral rehydration')).slice(0,3);
      return { type: 'ai', content: 'For dehydration, Oral Rehydration Salts (ORS) are recommended:', recommendations: ors };
    }

    // "When to use" intent
    const whenUseMatch = query.match(/when\s+to\s+use\s+([a-z0-9\s%]+)/);
    if (whenUseMatch) {
      const term = whenUseMatch[1].trim();
      const med = medicines.find(m => m.name.toLowerCase().includes(term) || m.activeIngredient?.toLowerCase().includes(term));
      if (med) {
        return {
          type: 'ai',
          content: `Use ${med.name} for ${
            med.category === 'Antihistamine' ? 'allergies (sneezing, runny nose, itching)'
            : med.category === 'Analgesic' ? 'pain and fever'
            : med.category === 'NSAID' ? 'pain, inflammation, and fever'
            : med.category === 'Antibiotic' ? 'bacterial infections (as prescribed)'
            : med.category === 'Proton Pump Inhibitor' ? 'acid reflux and heartburn'
            : med.category === 'Cardiovascular' ? 'blood pressure/heart conditions (doctor supervision)'
            : med.category === 'Statin' ? 'high cholesterol (doctor supervision)'
            : med.category === 'Antidiabetic' ? 'type 2 diabetes blood sugar control'
            : med.category === 'Insulin' ? 'blood glucose control per regimen'
            : 'its indicated condition'
          }. Always follow your doctor’s advice.`
        }
      }
    }

    if (query.includes("fever")) {
      const feverMeds = medicines.filter(med => 
        med.activeIngredient.toLowerCase().includes("paracetamol") ||
        med.name.toLowerCase().includes("paracetamol")
      ).slice(0, 3);
      
      return {
        type: "ai",
        content: "For fever, these medicines are commonly recommended:",
        recommendations: feverMeds
      };
    }

    if (query.includes("cough") || query.includes("cold")) {
      const coughMeds = medicines.filter(med => 
        med.category === "Antitussive" || med.category === "Bronchodilator" ||
        med.name.toLowerCase().includes("cough") || med.name.toLowerCase().includes("syrup")
      ).slice(0, 3);
      
      return {
        type: "ai",
        content: "For cough and cold symptoms, consider these medicines:",
        recommendations: coughMeds
      };
    }

    if (query.includes("antibiotic") || query.includes("infection")) {
      const antibiotics = medicines.filter(med => 
        med.category === "Antibiotic"
      ).slice(0, 3);
      
      return {
        type: "ai",
        content: "For bacterial infections, these antibiotics are available:",
        recommendations: antibiotics
      };
    }

    // General help
    if (query.includes("help") || query.includes("what can you do")) {
      return {
        type: "ai",
        content: "I can help you with:\n• Finding medicines by name or symptoms\n• Price comparisons (₹ INR)\n• Medicine recommendations by category\n• Information about active ingredients\n• Manufacturer details\n\nTry asking: 'Find medicine for fever' or 'Show me pain relief medicines'"
      };
    }

    // Default response
    return {
      type: "ai",
      content: "I understand you're asking about medicines. Could you be more specific? For example:\n• 'Find medicine for headache'\n• 'Show me antibiotics'\n• 'What's the price of paracetamol?'\n• 'Recommend medicine for fever'"
    };
  };

  const sendMessage = (text) => {
    if (!text.trim()) return;
    const userMessage = {
      id: Date.now(),
      type: "user",
      content: text,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);
    setIsTyping(true);
    setTimeout(() => {
      const aiResponse = getAIResponse(text);
      const responseMessage = {
        id: Date.now() + 1,
        ...aiResponse,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, responseMessage]);
      setIsTyping(false);
    }, 600);
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;
    const text = inputMessage;
    setInputMessage("");
    sendMessage(text);
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const getMessageIcon = (type) => {
    switch (type) {
      case "ai":
        return <Bot className="h-5 w-5 text-blue-500" />;
      case "user":
        return <MessageCircle className="h-5 w-5 text-green-500" />;
      default:
        return <Info className="h-5 w-5 text-gray-500" />;
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case "approved":
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case "recalled":
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Info className="h-4 w-4 text-yellow-500" />;
    }
  };

  return (
    <section id="ai-assistant" className="py-20 bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-6">
        <div className="text-center mb-12">
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
              <Sparkles className="h-6 w-6 text-white" />
            </div>
            <h2 className="text-4xl font-bold">AI Medicine Assistant</h2>
          </div>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Get intelligent recommendations and answers about medicines using our comprehensive database
          </p>
        </div>

        <div className="max-w-4xl mx-auto">
          <Card className="p-6 h-[600px] flex flex-col">
            {/* Chat Header */}
            <div className="flex items-center gap-3 pb-4 border-b border-border/50 mb-4">
              <Bot className="h-6 w-6 text-blue-500" />
              <div>
                <h3 className="font-semibold">Medicine Assistant</h3>
                <p className="text-sm text-muted-foreground">Powered by AI • Based on Indian Medicine Dataset</p>
              </div>
            </div>

            {/* Messages Area */}
            <ScrollArea ref={scrollAreaRef} className="flex-1 pr-4">
              <div className="space-y-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex gap-3 ${message.type === "user" ? "justify-end" : "justify-start"}`}
                  >
                    {message.type === "ai" && (
                      <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center shrink-0">
                        {getMessageIcon(message.type)}
                      </div>
                    )}
                    
                    <div className={`max-w-[80%] ${message.type === "user" ? "order-first" : ""}`}>
                      <div
                        className={`p-4 rounded-lg ${
                          message.type === "user"
                            ? "bg-blue-500 text-white"
                            : "bg-gray-100 text-gray-900"
                        }`}
                      >
                        <p className="whitespace-pre-wrap">{message.content}</p>
                        
                        {/* Medicine Recommendations */}
                        {message.recommendations && message.recommendations.length > 0 && (
                          <div className="mt-4 space-y-3">
                            {message.recommendations.map((med) => (
                              <Card key={med.id} className="p-3 bg-white border border-gray-200">
                                <div className="flex justify-between items-start mb-2">
                                  <div>
                                    <h4 className="font-semibold text-sm">{med.name}</h4>
                                    <p className="text-xs text-gray-600">{med.activeIngredient}</p>
                                  </div>
                                  <div className="flex items-center gap-2">
                                    {getStatusIcon(med.status)}
                                    <Badge variant="secondary" className="text-xs">
                                      {med.category}
                                    </Badge>
                                  </div>
                                </div>
                                
                                <div className="grid grid-cols-2 gap-2 text-xs">
                                  <div>
                                    <span className="text-gray-500">Manufacturer:</span>
                                    <p className="font-medium">{med.manufacturer}</p>
                                  </div>
                                  <div>
                                    <span className="text-gray-500">Price:</span>
                                    <p className="font-medium text-green-600">{med.price}</p>
                                  </div>
                                  <div>
                                    <span className="text-gray-500">Form:</span>
                                    <p>{med.dosageForm}</p>
                                  </div>
                                  <div>
                                    <span className="text-gray-500">Strength:</span>
                                    <p>{med.strength}</p>
                                  </div>
                                </div>
                                
                                {med.description && (
                                  <p className="text-xs text-gray-600 mt-2">{med.description}</p>
                                )}
                              </Card>
                            ))}
                            {/* Medical disclaimer for sensitive categories */}
                            <p className="text-xs text-amber-600 bg-amber-50 border border-amber-200 rounded-md p-2">
                              Note: Medicines in categories like Antibiotic, Cardiovascular, Statin, Antidiabetic, and Insulin should be taken only under medical supervision. This assistant does not replace professional medical advice.
                            </p>
                          </div>
                        )}
                      </div>
                      
                      <p className="text-xs text-muted-foreground mt-1">
                        {message.timestamp.toLocaleTimeString()}
                      </p>
                    </div>

                    {message.type === "user" && (
                      <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center shrink-0">
                        {getMessageIcon(message.type)}
                      </div>
                    )}
                  </div>
                ))}

                {/* Typing Indicator */}
                {isTyping && (
                  <div className="flex gap-3">
                    <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center shrink-0">
                      <Bot className="h-5 w-5 text-blue-500" />
                    </div>
                    <div className="bg-gray-100 p-4 rounded-lg">
                      <div className="flex gap-1">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0.1s" }}></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }}></div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </ScrollArea>

            {/* Input Area */}
            <div className="flex gap-3 pt-4 border-t border-border/50">
              <Input
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask about medicines, symptoms, prices, or get recommendations..."
                className="flex-1"
                disabled={isTyping}
              />
              <Button
                onClick={handleSendMessage}
                disabled={isTyping || !inputMessage.trim()}
                className="px-6"
              >
                <Send className="h-4 w-4" />
              </Button>
            </div>
          </Card>

          {/* Quick Actions */}
          <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-3">
            <Button
              variant="outline"
              onClick={() => sendMessage("Find medicine for fever")}
              className="text-sm"
            >
              <Pill className="mr-2 h-4 w-4" />
              Fever Medicine
            </Button>
            <Button
              variant="outline"
              onClick={() => sendMessage("Show me pain relief medicines")}
              className="text-sm"
            >
              <Pill className="mr-2 h-4 w-4" />
              Pain Relief
            </Button>
            <Button
              variant="outline"
              onClick={() => sendMessage("Recommend antibiotics")}
              className="text-sm"
            >
              <Pill className="mr-2 h-4 w-4" />
              Antibiotics
            </Button>
            <Button
              variant="outline"
              onClick={() => sendMessage("What can you help me with?")}
              className="text-sm"
            >
              <Sparkles className="mr-2 h-4 w-4" />
              Help
            </Button>
          </div>
        </div>
      </div>
    </section>
  );
};
