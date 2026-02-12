import React from 'react';
import { Helmet } from 'react-helmet';
import Hero from '@/components/Hero';
import KeySnapshots from '@/components/KeySnapshots';
import DataTables from '@/components/DataTables';
import IPOCategories from '@/components/IPOCategories';
import Disclaimer from '@/components/Disclaimer';

const Home = () => {
  return (
    <>
      <Helmet>
        <title>IPOshala - Home</title>
      </Helmet>
      <Hero />
      <KeySnapshots />
      <DataTables />
      <IPOCategories />
      <Disclaimer />
    </>
  );
};

export default Home;