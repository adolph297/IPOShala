# IPOShala Project

A comprehensive platform for tracking and analyzing Initial Public Offerings (IPOs). This project integrates real-time fetching from NSE, data storage in MongoDB, and a modern React frontend for visualization.

## Project Structure

- **[IPOShala](./IPOShala)**: The frontend application built with Vite, React, and Tailwind CSS.
- **[iposhala_test](./iposhala_test)**: A collection of Python scripts and utilities for data fetching, NSE integration, and database management.

## Key Features

- **Live IPO Tracking**: Fetches the latest IPO data directly from NSE.
- **Historical Data**: Maintains a searchable database of closed and upcoming IPOs.
- **Company Insights**: Integrated company descriptions and document links (RHP, Anchor papers, etc.).
- **Data Pipeline**: Robust Python-based scripts for mass data ingestion and cleaning.

## Getting Started

### Prerequisites

- Node.js (for Frontend)
- Python 3.x (for Scripts)
- MongoDB (Database)

### Setup

1. **Frontend**:
   ```bash
   cd IPOShala
   npm install
   npm run dev
   ```

2. **Backend/Scripts**:
   ```bash
   cd iposhala_test
   pip install -r requirements.txt (if applicable)
   ```

## Repository Information

- **Remote**: `https://github.com/adolph297/IPOShala.git`
