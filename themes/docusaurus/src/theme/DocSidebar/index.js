/**
 * Wraps the default DocSidebar to inject the TopologyCanvas graph at the top.
 * Uses Docusaurus Swizzle "wrap" pattern for safe theme extension.
 */
import React from 'react';
import DocSidebar from '@theme-original/DocSidebar';


export default function DocSidebarWrapper(props) {
  return (
    <>
      <DocSidebar {...props} />
    </>
  );
}


