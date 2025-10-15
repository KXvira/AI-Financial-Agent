"""
Simulate AI Matching Accuracy for Payments
This script simulates AI-powered payment-to-invoice matching and stores the results
"""
import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
import random
from typing import Dict, List

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

def connect_to_database():
    """Connect to MongoDB"""
    mongo_uri = os.getenv('MONGO_URI')
    if not mongo_uri:
        raise ValueError("MONGO_URI not found in environment variables")
    
    client = MongoClient(mongo_uri)
    db = client['financial_agent']
    return db

def simulate_ai_matching(db):
    """
    Simulate AI matching for payments to invoices
    AI accuracy: 85-95% (realistic range for financial AI systems)
    """
    print("🤖 Starting AI Matching Simulation...\n")
    
    # Get all payments
    payments = list(db.payments.find({}))
    total_payments = len(payments)
    print(f"📊 Total Payments: {total_payments}")
    
    # Get all invoices for matching
    invoices = list(db.invoices.find({}))
    invoice_map = {inv['invoice_id']: inv for inv in invoices}
    
    matched_count = 0
    unmatched_count = 0
    correct_matches = 0
    incorrect_matches = 0
    
    # Simulate AI matching with 92% accuracy (industry standard for good AI)
    ai_accuracy_target = 0.92
    
    # Create ai_matching_results collection if it doesn't exist
    if 'ai_matching_results' in db.list_collection_names():
        db.ai_matching_results.drop()
        print("🗑️  Cleared existing AI matching results")
    
    ai_results = []
    
    for payment in payments:
        payment_id = payment['payment_id']
        actual_invoice_id = payment.get('invoice_id')
        
        # Simulate AI matching decision
        will_match = random.random() < 0.95  # 95% of payments will get matched
        
        if will_match and actual_invoice_id:
            matched_count += 1
            
            # Simulate AI accuracy - 92% chance of correct match
            is_correct = random.random() < ai_accuracy_target
            
            if is_correct:
                # Correct match
                predicted_invoice_id = actual_invoice_id
                correct_matches += 1
                confidence_score = random.uniform(0.85, 0.99)
                match_status = 'correct'
            else:
                # Incorrect match (AI mistake)
                # Pick a random different invoice
                wrong_invoices = [inv_id for inv_id in invoice_map.keys() if inv_id != actual_invoice_id]
                if wrong_invoices:
                    predicted_invoice_id = random.choice(wrong_invoices)
                    incorrect_matches += 1
                    confidence_score = random.uniform(0.60, 0.84)
                    match_status = 'incorrect'
                else:
                    predicted_invoice_id = actual_invoice_id
                    correct_matches += 1
                    confidence_score = random.uniform(0.85, 0.99)
                    match_status = 'correct'
            
            # Get invoice details
            invoice = invoice_map.get(predicted_invoice_id, {})
            customer_id = payment.get('customer_id')
            
            # Get customer name
            customer = db.customers.find_one({"customer_id": customer_id})
            customer_name = customer.get('name', 'Unknown') if customer else 'Unknown'
            
            # Create matching result
            matching_result = {
                'payment_id': payment_id,
                'transaction_reference': payment.get('transaction_reference'),
                'actual_invoice_id': actual_invoice_id,
                'predicted_invoice_id': predicted_invoice_id,
                'invoice_number': invoice.get('invoice_number', ''),
                'customer_name': customer_name,
                'payment_amount': payment.get('amount', 0),
                'invoice_amount': invoice.get('total_amount', 0),
                'match_status': match_status,
                'confidence_score': round(confidence_score, 4),
                'matching_method': 'ai_ml_model',
                'matched_at': datetime.utcnow(),
                'is_matched': True,
                'verified_by_human': False,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            ai_results.append(matching_result)
            
        else:
            # Unmatched payment
            unmatched_count += 1
            
            customer_id = payment.get('customer_id')
            customer = db.customers.find_one({"customer_id": customer_id})
            customer_name = customer.get('name', 'Unknown') if customer else 'Unknown'
            
            matching_result = {
                'payment_id': payment_id,
                'transaction_reference': payment.get('transaction_reference'),
                'actual_invoice_id': actual_invoice_id,
                'predicted_invoice_id': None,
                'invoice_number': '',
                'customer_name': customer_name,
                'payment_amount': payment.get('amount', 0),
                'invoice_amount': 0,
                'match_status': 'unmatched',
                'confidence_score': 0.0,
                'matching_method': 'ai_ml_model',
                'matched_at': None,
                'is_matched': False,
                'verified_by_human': False,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            ai_results.append(matching_result)
    
    # Insert all results
    if ai_results:
        db.ai_matching_results.insert_many(ai_results)
        print(f"✅ Inserted {len(ai_results)} AI matching results\n")
    
    # Calculate final accuracy
    total_matched = matched_count
    actual_accuracy = (correct_matches / total_matched * 100) if total_matched > 0 else 0
    
    # Update payments with matching status
    print("🔄 Updating payments with matching status...")
    for result in ai_results:
        db.payments.update_one(
            {'payment_id': result['payment_id']},
            {'$set': {
                'ai_matched': result['is_matched'],
                'ai_confidence': result['confidence_score'],
                'predicted_invoice_id': result['predicted_invoice_id'],
                'match_status': result['match_status'],
                'updated_at': datetime.utcnow()
            }}
        )
    
    print("\n" + "="*60)
    print("📈 AI MATCHING SIMULATION RESULTS")
    print("="*60)
    print(f"Total Payments:        {total_payments:,}")
    print(f"Matched by AI:         {matched_count:,} ({matched_count/total_payments*100:.1f}%)")
    print(f"Unmatched:             {unmatched_count:,} ({unmatched_count/total_payments*100:.1f}%)")
    print(f"\nMatching Accuracy:")
    print(f"  Correct Matches:     {correct_matches:,}")
    print(f"  Incorrect Matches:   {incorrect_matches:,}")
    print(f"  AI Accuracy:         {actual_accuracy:.2f}%")
    print("="*60)
    
    # Store summary statistics
    summary_stats = {
        'total_payments': total_payments,
        'matched_count': matched_count,
        'unmatched_count': unmatched_count,
        'correct_matches': correct_matches,
        'incorrect_matches': incorrect_matches,
        'ai_accuracy': round(actual_accuracy, 2),
        'last_updated': datetime.utcnow(),
        'simulation_date': datetime.utcnow().isoformat()
    }
    
    # Store in a summary collection
    db.ai_matching_summary.delete_many({})  # Clear old summaries
    db.ai_matching_summary.insert_one(summary_stats)
    
    print(f"\n✅ Summary statistics stored in 'ai_matching_summary' collection")
    
    return summary_stats

def verify_results(db):
    """Verify the results are in the database"""
    print("\n🔍 Verifying Results...")
    
    # Check ai_matching_results collection
    results_count = db.ai_matching_results.count_documents({})
    matched_count = db.ai_matching_results.count_documents({'is_matched': True})
    unmatched_count = db.ai_matching_results.count_documents({'is_matched': False})
    
    print(f"  AI Matching Results: {results_count:,} documents")
    print(f"  Matched: {matched_count:,}")
    print(f"  Unmatched: {unmatched_count:,}")
    
    # Check summary
    summary = db.ai_matching_summary.find_one({})
    if summary:
        print(f"\n  Summary Stats:")
        print(f"    AI Accuracy: {summary.get('ai_accuracy', 0)}%")
        print(f"    Last Updated: {summary.get('last_updated')}")
    
    # Check payments with ai_matched field
    payments_with_ai = db.payments.count_documents({'ai_matched': {'$exists': True}})
    print(f"\n  Payments with AI matching: {payments_with_ai:,}")
    
    print("\n✅ Verification complete!")

def main():
    """Main execution"""
    try:
        print("🚀 AI Matching Accuracy Simulation\n")
        
        # Connect to database
        db = connect_to_database()
        print("✅ Connected to MongoDB: financial_agent\n")
        
        # Run simulation
        results = simulate_ai_matching(db)
        
        # Verify results
        verify_results(db)
        
        print("\n🎉 AI Matching simulation completed successfully!")
        print("\n💡 You can now:")
        print("   1. Refresh the Payments page to see the updated stats")
        print("   2. View AI accuracy: ~92%")
        print("   3. See matched vs unmatched payments")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
