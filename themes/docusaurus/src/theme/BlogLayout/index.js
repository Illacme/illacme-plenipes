import React from 'react';
import clsx from 'clsx';
import Layout from '@theme/Layout';
import BlogSidebar from '@theme/BlogSidebar';
import TopologyCanvas from '@site/src/components/TopologyCanvas';

export default function BlogLayout(props) {
  const {sidebar, toc, children, ...layoutProps} = props;
  const hasSidebar = sidebar && sidebar.items.length > 0;
  
  return (
    <Layout {...layoutProps}>
      <div className="container margin-vert--lg">
        <div className="row">
          <BlogSidebar sidebar={sidebar} />
          <main
            className={clsx('col', {
              'col--6': hasSidebar,
              'col--9 col--offset-1': !hasSidebar,
            })}>
            {children}
          </main>
          
          {/* Always show the right column for the graph in Blog pages */}
          <div className="col col--3">
            {/* Always render the relationship graph on TOP */}
            <div style={{ marginBottom: toc ? '2rem' : '0' }}>
              <TopologyCanvas height={250} />
            </div>
            {toc}
          </div>
        </div>
      </div>

    </Layout>
  );
}
